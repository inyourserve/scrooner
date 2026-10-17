#!/bin/zsh
set -euo pipefail

script_dir=${0:A:h}
admin_dir=${script_dir:h}
repo_dir=${admin_dir:h:h}

set -a
source "${repo_dir}/pipeline/.env"
if [[ -f "${admin_dir}/.env" ]]; then
  source "${admin_dir}/.env"
fi
set +a

export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
export DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8100
export WAREHOUSE_DATABASE_URL="${DATABASE_URL}"

cd "${admin_dir}"
exec .venv/bin/python manage.py runserver 127.0.0.1:8100
