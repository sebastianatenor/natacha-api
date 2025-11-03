import datetime
import subprocess


def now():
    return datetime.datetime.utcnow().isoformat()


def run_cmd(cmd):
    """Ejecuta un comando en shell y devuelve True/False + salida."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip()


def ensure_secret(name):
    ok, _ = run_cmd(f"gcloud secrets describe {name} --project=asistente-sebastian")
    if not ok:
        print(f"[CREATING SECRET] {name}")
        run_cmd(
            f"gcloud secrets create {name} --replication-policy='automatic' --project=asistente-sebastian"
        )
        return False
    return True


def ensure_scheduler_job(name, schedule, uri, service_account):
    ok, _ = run_cmd(
        f"gcloud scheduler jobs describe {name} --region=us-central1 --project=asistente-sebastian"
    )
    if not ok:
        print(f"[CREATING SCHEDULER JOB] {name}")
        run_cmd(
            f"gcloud scheduler jobs create http {name} "
            f"--schedule='{schedule}' --uri='{uri}' --http-method=POST "
            f"--oidc-service-account-email={service_account} "
            f"--project=asistente-sebastian --region=us-central1"
        )
        return False
    return True


def ensure_pubsub_topic(topic):
    ok, _ = run_cmd(
        f"gcloud pubsub topics describe {topic} --project=asistente-sebastian"
    )
    if not ok:
        print(f"[CREATING PUB/SUB TOPIC] {topic}")
        run_cmd(f"gcloud pubsub topics create {topic} --project=asistente-sebastian")
        return False
    return True


def ensure_run_service_account(service, account):
    ok, _ = run_cmd(
        f"gcloud run services describe {service} --region=us-central1 --project=asistente-sebastian | grep {account}"
    )
    if not ok:
        print(f"[UPDATING SERVICE ACCOUNT] {service} -> {account}")
        run_cmd(
            f"gcloud run services update {service} "
            f"--service-account={account} "
            f"--region=us-central1 --project=asistente-sebastian"
        )
        return False
    return True
