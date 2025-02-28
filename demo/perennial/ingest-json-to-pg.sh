set -euo pipefail
script_dir=$(dirname "$(readlink -f "$0")")

echo "loading collection.json"

pypgstac load collections \
  "${script_dir}/soc_stac_catalog/collection.json" \
    --dsn postgresql://username:password@0.0.0.0:5439/postgis \
    --method upsert

count=0
total=$(find ./soc_stac_catalog -mindepth 2 -type f -name "*.json" | wc -l)
echo "$total item files found to load"

find ./soc_stac_catalog -mindepth 2 -type f -name "*.json" | while read -r file; do
  ((count++))
  if ((count % 10 == 0)); then
    echo "Processed $count of $total"
  fi
  pypgstac load items "$file" \
    --dsn postgresql://username:password@0.0.0.0:5439/postgis \
    --method upsert
done

echo "STAC Browser:"
echo "http://localhost:8085"
