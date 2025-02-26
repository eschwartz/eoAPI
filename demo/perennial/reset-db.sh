set -euo pipefail

script_dir=$(dirname "$(readlink -f "$0")")

dir=$(realpath "${script_dir}/../../.pgdata")

# Confirmation prompt
echo "Delete db volume directory at $dir?"
read -p " (y/n): " confirmation_prompt
if [[ ! ${confirmation_prompt} =~ ^[Yy]$ ]]; then
  echo "Script execution aborted."
  exit 1
fi

cd "$script_dir/../../"
docker compose down -v
rm -rf "$dir"
docker compose up -d
docker compose logs -f
