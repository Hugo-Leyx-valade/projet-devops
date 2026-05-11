"""Tests Testinfra pour valider le déploiement complet."""
import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


# ---------------------------------------------------------------------------
# Nginx (reverse proxy)
# ---------------------------------------------------------------------------
def test_nginx_running_and_enabled(host):
    svc = host.service("nginx")
    assert svc.is_running
    assert svc.is_enabled


def test_nginx_listening_80(host):
    assert host.socket("tcp://0.0.0.0:80").is_listening


def test_nginx_status_listening_8080(host):
    assert host.socket("tcp://0.0.0.0:8080").is_listening


def test_nginx_fastapi_vhost_deployed(host):
    vhost = host.file("/etc/nginx/sites-enabled/fastapi.conf")
    assert vhost.exists
    assert vhost.is_symlink


# ---------------------------------------------------------------------------
# FastAPI (application)
# ---------------------------------------------------------------------------
def test_fastapi_service_running_and_enabled(host):
    svc = host.service("fastapi")
    assert svc.is_running
    assert svc.is_enabled


def test_fastapi_listening_on_8000(host):
    assert host.socket("tcp://127.0.0.1:8000").is_listening


def test_fastapi_user_exists(host):
    user = host.user("fastapi")
    assert user.exists
    assert user.group == "fastapi"


def test_fastapi_venv_present(host):
    uvicorn_bin = host.file("/opt/fastapi/venv/bin/uvicorn")
    assert uvicorn_bin.exists
    assert uvicorn_bin.mode & 0o111  # exécutable


def test_fastapi_env_file(host):
    env_file = host.file("/etc/fastapi/fastapi.env")
    assert env_file.exists
    assert env_file.contains("APP_NAME")


def test_fastapi_health_via_local(host):
    cmd = host.run("curl -fsS http://127.0.0.1:8000/health")
    assert cmd.rc == 0
    assert '"status":"healthy"' in cmd.stdout


def test_fastapi_health_via_nginx(host):
    cmd = host.run("curl -fsS http://127.0.0.1/health")
    assert cmd.rc == 0
    assert '"status":"healthy"' in cmd.stdout


# ---------------------------------------------------------------------------
# MySQL (base de données)
# ---------------------------------------------------------------------------
def test_mysql_running_and_enabled(host):
    svc = host.service("mysql")
    assert svc.is_running
    assert svc.is_enabled


def test_mysql_socket_exists(host):
    assert host.socket("unix:///var/run/mysqld/mysqld.sock").is_listening


def test_mysql_database_exists(host):
    cmd = host.run(
        "mysql -N -e \"SHOW DATABASES LIKE 'fastapi_db';\""
    )
    assert cmd.rc == 0
    assert "fastapi_db" in cmd.stdout


def test_mysql_user_exists(host):
    cmd = host.run(
        "mysql -N -e \"SELECT User FROM mysql.user WHERE User='fastapi_user';\""
    )
    assert cmd.rc == 0
    assert "fastapi_user" in cmd.stdout
