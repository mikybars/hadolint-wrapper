#!/usr/bin/env bash
#
# Usage:
#
# upload-github-release-asset.sh stefanbuck/playground v0.1.0 ./build.zip TOKEN
#

set -euo pipefail

OK=200
CREATED=201
UNAUTHORIZED=401
NOT_FOUND=404

repo=$1
tag=$2
filename=$3
github_api_token=$4

GH_API="https://api.github.com"
GH_REPO="$GH_API/repos/$repo"
GH_TAGS="$GH_REPO/releases/tags/$tag"
AUTH="Authorization: token $github_api_token"

response=$(mktemp || exit 1)

cleanup() {
	rm -f "$response"
}
trap cleanup EXIT
trap cleanup ERR

verify_token() {
	echo -n "Verifying token... "

	http_code=$(curl -s \
		--header "$AUTH" \
		--output "$response" \
		--write-out "%{http_code}" \
		"$GH_REPO"
	)

	if (( http_code != OK )); then
		if (( http_code == UNAUTHORIZED )); then
			echo "unauthorized"
		else
			echo "ko"
			echo "http_code: $http_code"
			cat $response
		fi
		exit 2
	fi

	echo "ok"
}

get_release_id() {
	http_code=$(curl -s \
		--header "$AUTH" \
		--output "$response" \
		--write-out "%{http_code}" \
		"$GH_TAGS"
	)
	
	if (( http_code == NOT_FOUND )); then
		echo "not found"
	elif (( http_code != OK )); then
		echo "ko"
	else
		jq '.id' <"$response"
	fi
}

upload_asset() {
	local release_id=$1

	echo -n "Uploading file $(basename $filename)... "

	http_code=$(curl -s \
		--data-binary @"$filename" \
		--header "$AUTH" \
		--header "Content-Type: application/octet-stream" \
		--output "$response" \
		--write-out "%{http_code}" \
		"https://uploads.github.com/repos/$repo/releases/$release_id/assets?name=$(basename $filename)"
	)

	if (( http_code != CREATED )); then
		echo "ko"
		exit 4
	fi

	echo "ok"
	echo "Asset URL: $(jq '.browser_download_url' <$response)"
}

is_a_number() {
	[[ $1 =~ ^[0-9]+$ ]]
}

verify_token

echo -n "Fetching release id... "
release_id=$(get_release_id)
echo "$release_id"
if ! is_a_number $release_id; then
	exit 3
fi

upload_asset $release_id
