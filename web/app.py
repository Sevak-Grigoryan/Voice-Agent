"""Web page for voice_agent: open http://localhost:7860, give a voice and a text, get the audio back.

    python -m web.app
"""
import io
import json
import os
import queue
import shutil
import tempfile
import threading
import time
import uuid

from flask import Flask, jsonify, request, send_file, send_from_directory

from core.voice_agent import DEFAULT_VARIANT, VARIANTS, Cancelled, VoiceAgent, encode_mp3, prepare_voice, write_wav

HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(HERE, "static"))
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024  # voice uploads up to 60 MB

agents = {}          # variant -> loaded VoiceAgent, so each model is loaded only once
jobs = {}            # job id -> dict with state and progress, read by the page
work = queue.Queue() # jobs run one at a time, the model isn't thread safe
MAX_KEPT_JOBS = 20


def get_agent(variant):
    if variant not in agents:
        agents[variant] = VoiceAgent(variant)
    return agents[variant]


def run_job(job):
    job["started"] = time.time()
    try:
        job["state"] = "loading"
        agent = get_agent(job["variant"])
        job["state"] = "working"

        def progress(done, total, piece):
            job.update(done=done, total=total, piece=piece)

        audio = agent.speak(job.pop("voice_path"), job.pop("text"), clean=False,
                            on_progress=progress, should_stop=lambda: job["cancel"])
        job["mp3"] = encode_mp3(audio, agent.sample_rate)
        job["seconds"] = round(len(audio) / agent.sample_rate, 1)
        job["state"] = "done"
    except Cancelled:
        job["state"] = "cancelled"
    except ValueError as e:
        job.update(state="error", error=str(e))
    except Exception as e:  # show the real reason on the page instead of hanging
        app.logger.exception("generation failed")
        job.update(state="error", error=f"Something went wrong: {e}")
    finally:
        shutil.rmtree(job["tmp"], ignore_errors=True)


def worker():
    while True:
        job = work.get()
        if not job["cancel"]:
            run_job(job)
        else:
            job["state"] = "cancelled"


threading.Thread(target=worker, daemon=True).start()


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/status")
def status():
    return jsonify(loaded=list(agents), variants=list(VARIANTS), default=DEFAULT_VARIANT)


@app.post("/api/voice")
def voice():
    """Cleans the uploaded voice and keeps its best part. The page plays it back and sends it with the text."""
    upload = request.files.get("voice")
    if not upload:
        return jsonify(error="Please add a voice recording first."), 400
    clean = request.form.get("clean", "1") == "1"
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "voice.wav")
        upload.save(path)
        try:
            samples, info = prepare_voice(path, tmp, clean=clean)
        except Exception as e:
            app.logger.exception("voice preparation failed")
            return jsonify(error=f"Couldn't prepare this voice: {e}"), 400
    buf = io.BytesIO()
    write_wav(buf, samples)
    buf.seek(0)
    response = send_file(buf, mimetype="audio/wav")
    response.headers["X-Voice-Info"] = json.dumps(info)
    return response


@app.post("/api/speak")
def speak():
    upload = request.files.get("voice")
    text = (request.form.get("text") or "").strip()
    variant = request.form.get("variant") or DEFAULT_VARIANT
    if not upload:
        return jsonify(error="Please add a voice recording first."), 400
    if not text:
        return jsonify(error="Please write the text you want to hear."), 400
    if variant not in VARIANTS:
        return jsonify(error=f"Unknown model: {variant}"), 400

    tmp = tempfile.mkdtemp(prefix="voice_job_")
    voice_path = os.path.join(tmp, "voice.wav")
    upload.save(voice_path)

    for old in sorted(jobs.values(), key=lambda j: j["created"])[:-MAX_KEPT_JOBS]:
        if old["state"] in ("done", "error", "cancelled"):
            jobs.pop(old["id"], None)

    job_id = uuid.uuid4().hex
    jobs[job_id] = {"id": job_id, "state": "queued", "created": time.time(), "variant": variant, "tmp": tmp,
                    "voice_path": voice_path, "text": text, "done": 0, "total": 0, "piece": "", "cancel": False}
    work.put(jobs[job_id])
    return jsonify(job=job_id)


@app.get("/api/jobs/<job_id>")
def job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify(error="This job is gone. Please create the audio again."), 404
    out = {k: job.get(k) for k in ("state", "done", "total", "piece", "error", "seconds")}
    out["queued_before"] = sum(1 for j in jobs.values() if j["state"] == "queued" and j["created"] < job["created"])
    if job["state"] == "working" and job["done"]:
        per_piece = (time.time() - job["started"]) / job["done"]
        out["eta"] = round(per_piece * (job["total"] - job["done"]))
    return jsonify(out)


@app.post("/api/jobs/<job_id>/cancel")
def cancel(job_id):
    job = jobs.get(job_id)
    if job:
        job["cancel"] = True
    return jsonify(ok=True)


@app.get("/api/jobs/<job_id>/audio")
def job_audio(job_id):
    job = jobs.get(job_id)
    if not job or job["state"] != "done":
        return jsonify(error="The audio isn't ready."), 404
    return send_file(io.BytesIO(job["mp3"]), mimetype="audio/mpeg", download_name="voice_agent.mp3")


if __name__ == "__main__":
    print("Open http://localhost:7860 in your browser")
    app.run(host="127.0.0.1", port=7860, threaded=True)
