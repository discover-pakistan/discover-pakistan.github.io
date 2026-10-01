import os
import time
import subprocess
import requests
import tempfile
import imageio_ffmpeg
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN = (os.getenv("ACCESS_TOKEN") or "").strip()
THREAD_TOKEN = (os.getenv("THREAD_TOKEN") or "").strip()
FB_PAGE_ID = (os.getenv("FB_PAGE_ID") or "").strip()
IG_BUSINESS_ACCOUNT_ID = (os.getenv("IG_BUSINESS_ACCOUNT_ID") or "").strip()
THREADS_USER_ID = (os.getenv("THREADS_USER_ID") or "").strip()
API_VERSION = (os.getenv("API_VERSION") or "v19.0").strip()

BASE_URL = "https://graph.facebook.com"
THREADS_BASE_URL = "https://graph.threads.net"

def resolve_video_url(url, max_retries=10, delay=10):
    """
    Resolves redirects and waits for the URL to become publicly accessible (200 OK).
    Helpful for hosts like GitHub or Dropbox that use redirects and CDN propagation.
    """
    final_url = url
    if "github.com" in url and "/raw/" in url:
        # Convert to direct CDN URL immediately to avoid one redirect layer
        # https://github.com/user/repo/raw/main/path -> https://raw.githubusercontent.com/user/repo/main/path
        final_url = url.replace("github.com", "raw.githubusercontent.com").replace("/raw/", "/")
        print(f"[*] Using direct CDN URL: {final_url}")

    print(f"[*] Verifying video accessibility for: {final_url}")
    
    for i in range(max_retries):
        try:
            # Use GET for the first byte instead of HEAD if HEAD is restricted, 
            # but usually HEAD is fine for CDNs.
            res = requests.head(final_url, allow_redirects=True, timeout=15)
            if res.status_code == 200:
                if i > 0:
                    print(f"[+] URL is now accessible (Attempt {i+1}).")
                return res.url
            else:
                print(f"[*] Attempt {i+1}: Received {res.status_code}. Waiting {delay}s for propagation...")
        except Exception as e:
            print(f"[*] Attempt {i+1}: Error checking URL: {e}. Waiting {delay}s...")
        
        time.sleep(delay)
    
    print(f"[!] Warning: URL still not returning 200 OK after {max_retries} attempts. Proceeding anyway...")
    return final_url

def get_page_access_token(page_id):
    """
    Attempts to get a Page Access Token using the provided User/System User token.
    Required for publishing to Facebook Pages.
    """
    print(f"[*] Attempting to fetch Page Access Token for {page_id}...")
    url = f"{BASE_URL}/{API_VERSION}/{page_id}"
    params = {
        "fields": "access_token",
        "access_token": ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params=params).json()
        if "access_token" in response:
            print("[+] Successfully obtained Page Access Token.")
            return response["access_token"]
        else:
            print(f"[-] Could not get Page Access Token: {response}")
            return ACCESS_TOKEN # Fallback to original token
    except Exception as e:
        print(f"[-] Error fetching Page Access Token: {e}")
        return ACCESS_TOKEN

def check_status(container_id, platform="instagram", token=None):
    """
    Polls the container status until it's ready or fails.
    """
    use_token = token or ACCESS_TOKEN
    
    if platform == "instagram":
        url = f"{BASE_URL}/{API_VERSION}/{container_id}"
        params = {"fields": "status_code"}
    else: # Threads
        url = f"{THREADS_BASE_URL}/v1.0/{container_id}"
        params = {"fields": "status,error_message"}
    
    headers = {
        "Authorization": f"Bearer {use_token}"
    }
    
    print(f"[*] Checking {platform} container status for {container_id}...")
    
    for _ in range(30):  # Wait up to 5 minutes (30 * 10s)
        try:
            response = requests.get(url, headers=headers, params=params).json()
            
            if platform == "instagram":
                status = response.get("status_code")
                if status == "FINISHED":
                    print("[+] Instagram container ready.")
                    return True
                elif status == "ERROR":
                    print(f"[-] Instagram error: {response}")
                    return False
                else:
                    print(f"[*] Instagram status: {status}...")
            else: # Threads
                status = response.get("status")
                # Threads uses FINISHED or PUBLISHED depending on the phase
                if status in ["FINISHED", "PUBLISHED"]:
                    print(f"[+] Threads container ready ({status}).")
                    return True
                elif status == "ERROR" or "error_message" in response:
                    print(f"[-] Threads error: {response}")
                    return False
                else:
                    if status is None:
                        print(f"[*] Threads status is missing. Full response: {response}")
                    else:
                        print(f"[*] Threads status: {status}...")
        except Exception as e:
            print(f"[-] Error checking status: {e}")
            
        time.sleep(10)
    
    print("[-] Polling timed out.")
    return False

def _reencode_for_instagram(input_path: str) -> str:
    """
    Re-encodes a video to studio-grade Instagram/FB compliant specs:
      - Video: H.264 (libx264), 'high' profile, yuv420p pixel format, CRF 18 (8-12 Mbps)
      - Audio: AAC 192kbps, 44100 Hz stereo
      - Faststart moov atom for streaming
    Returns path to the re-encoded file (caller must delete it).
    """
    output_path = input_path.replace(".mp4", "_ig.mp4")
    if Path(input_path).suffix != ".mp4":
        output_path = input_path + "_ig.mp4"

    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ffmpeg_exe = "ffmpeg"

    cmd = [
        ffmpeg_exe, "-y",
        "-i", input_path,
        "-vcodec", "libx264",
        "-profile:v", "high",
        "-level", "4.1",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-g", "60",
        "-b:v", "8000k",
        "-maxrate", "12000k",
        "-bufsize", "16000k",
        "-acodec", "aac",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]
    print(f"[*] Re-encoding video for Instagram studio compliance (8M-12M CRF18)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[-] ffmpeg re-encode failed:\n{result.stderr[-500:]}")
        return input_path  # Fall back to original
    print(f"[+] Re-encoded studio master: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path


def _instagram_resumable_upload(upload_path, file_size, container_id, max_retries=2):
    """
    Performs the actual binary upload to Instagram's rupload endpoint.
    Uses OAuth auth (not Bearer) as required by rupload.facebook.com.
    Returns True on success, False on failure.
    """
    for attempt in range(max_retries):
        upload_url = f"https://rupload.facebook.com/ig-api-upload/{API_VERSION}/{container_id}"
        upload_headers = {
            "Authorization": f"OAuth {ACCESS_TOKEN}",  # rupload requires OAuth, NOT Bearer
            "offset": "0",
            "file_size": str(file_size),
            "Content-Type": "application/octet-stream",
        }
        
        with open(upload_path, "rb") as f:
            upload_res = requests.post(upload_url, headers=upload_headers, data=f)
        
        print(f"[*] Instagram upload response: HTTP {upload_res.status_code}")
        
        if upload_res.status_code == 200:
            try:
                body = upload_res.json()
                if body.get("debug_info", {}).get("type") == "ProcessingFailedError":
                    print(f"[-] Upload accepted but processing failed (attempt {attempt+1}): {body}")
                    if attempt < max_retries - 1:
                        print(f"[*] Retrying in 5 seconds...")
                        time.sleep(5)
                        continue
                    return False
            except ValueError:
                pass  # Not JSON, that's fine
            print(f"[+] Instagram binary upload succeeded.")
            return True
        else:
            print(f"[-] Instagram binary upload failed (HTTP {upload_res.status_code}, attempt {attempt+1}): {upload_res.text}")
            if attempt < max_retries - 1:
                print(f"[*] Retrying in 5 seconds...")
                time.sleep(5)
    
    return False


def publish_instagram_reel(video_source, caption):
    """
    Publishes a Reel to Instagram using Resumable Binary Upload.
    video_source can be a local file path or a URL.
    Videos are re-encoded to strict Instagram specs before upload.
    """
    if not IG_BUSINESS_ACCOUNT_ID:
        print("[!] IG_BUSINESS_ACCOUNT_ID missing. Skipping Instagram.")
        return

    video_path = None
    reencoded_path = None
    if video_source.startswith("http"):
        print(f"[*] Downloading video from URL for Instagram upload...")
        try:
            with requests.get(video_source, stream=True, allow_redirects=True) as r:
                r.raise_for_status()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                    for chunk in r.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
                    video_path = tmp_file.name
        except Exception as e:
            print(f"[-] Failed to download video: {e}")
            return
    else:
        video_path = video_source

    try:
        # Re-encode to guaranteed Instagram-compatible specs
        reencoded_path = _reencode_for_instagram(video_path)
        upload_path = reencoded_path
        file_size = os.path.getsize(upload_path)

        # Step 1: Create media container
        print("[*] Initializing Instagram Resumable upload...")
        url = f"{BASE_URL}/{API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        payload = {
            "media_type": "REELS",
            "upload_type": "resumable",
            "caption": caption,
            "share_to_feed": "true"  # Ensure it appears on the main profile grid/feed
        }
        
        response = requests.post(url, headers=headers, data=payload).json()
        container_id = response.get("id")
        
        if not container_id:
            print(f"[-] Failed to create Instagram container: {response}")
            return

        print(f"[+] Container created: {container_id}")

        # Step 2: Upload binary data via rupload
        if not _instagram_resumable_upload(upload_path, file_size, container_id):
            print("[-] Instagram upload failed after all retries.")
            return

        # Step 3: Poll and Publish
        if check_status(container_id, "instagram"):
            print("[*] Publishing Instagram Reel...")
            publish_url = f"{BASE_URL}/{API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media_publish"
            publish_payload = {"creation_id": container_id}
            res = requests.post(publish_url, headers=headers, data=publish_payload).json()
            print(f"[+] Instagram Response: {res}")

    finally:
        if video_source.startswith("http") and video_path and os.path.exists(video_path):
            os.remove(video_path)
        if reencoded_path and reencoded_path != video_path and os.path.exists(reencoded_path):
            os.remove(reencoded_path)

def publish_instagram_carousel(image_urls, caption):
    """
    Publishes a Carousel (Sidecar) to Instagram.
    image_urls: List of publicly accessible image URLs.
    """
    if not IG_BUSINESS_ACCOUNT_ID:
        print("[!] IG_BUSINESS_ACCOUNT_ID missing. Skipping Instagram Carousel.")
        return

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    # Step 1: Create individual item containers
    child_ids = []
    print(f"[*] Creating {len(image_urls)} carousel item containers...")
    for url in image_urls:
        # Resolve GitHub raw URLs if necessary
        resolved_url = resolve_video_url(url)
        
        payload = {
            "image_url": resolved_url,
            "is_carousel_item": "true"
        }
        create_url = f"{BASE_URL}/{API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media"
        res = requests.post(create_url, headers=headers, data=payload).json()
        item_id = res.get("id")
        if item_id:
            child_ids.append(item_id)
            print(f"    [+] Created item container: {item_id}")
        else:
            print(f"    [-] Failed to create item container for {url}: {res}")

    if not child_ids:
        print("[-] No items were created. Aborting carousel.")
        return

    # Step 2: Create the main CAROUSEL container
    print("[*] Initializing Carousel container...")
    carousel_payload = {
        "media_type": "CAROUSEL",
        "caption": caption,
        "children": ",".join(child_ids)
    }
    carousel_url = f"{BASE_URL}/{API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media"
    res = requests.post(carousel_url, headers=headers, data=carousel_payload).json()
    carousel_container_id = res.get("id")

    if not carousel_container_id:
        print(f"[-] Failed to create Carousel container: {res}")
        return

    # Step 3: Poll and Publish
    # Note: For carousels, we usually wait a bit for items to process
    print("[*] Waiting for carousel items to process...")
    time.sleep(15) 

    if check_status(carousel_container_id, "instagram"):
        print("[*] Publishing Instagram Carousel...")
        publish_url = f"{BASE_URL}/{API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media_publish"
        publish_payload = {"creation_id": carousel_container_id}
        res = requests.post(publish_url, headers=headers, data=publish_payload).json()
        print(f"[+] Instagram Carousel Response: {res}")

def publish_facebook_reel(video_path, caption, title="Holy Quran Reflection"):
    """
    Publishes a Reel to a Facebook Page using Resumable Binary Upload.
    Supports local file paths.
    """
    if not FB_PAGE_ID:
        print("[!] FB_PAGE_ID missing. Skipping Facebook.")
        return

    # For Facebook Pages, we almost always need a Page Access Token
    page_token = get_page_access_token(FB_PAGE_ID)
    headers = {
        "Authorization": f"Bearer {page_token}"
    }

    try:
        file_size = os.path.getsize(video_path)
        print(f"[*] Initializing Facebook Reel session ({file_size} bytes)...")
        # Step 1: Start
        url = f"{BASE_URL}/{API_VERSION}/{FB_PAGE_ID}/video_reels"
        payload = {
            "upload_phase": "start"
        }
        res = requests.post(url, headers=headers, data=payload).json()
        video_id = res.get("video_id")
        upload_url = res.get("upload_url")
        
        if not video_id:
            print(f"[-] Failed to start Facebook Reel: {res}")
            return

        # Step 2: Upload Binary Data
        print("[*] Uploading binary data to Facebook...")
        # Note: Facebook resumable upload uses rupload.facebook.com
        # The upload_url returned in Step 1 is already formatted correctly
        upload_headers = {
            "Authorization": f"OAuth {page_token}",
            "offset": "0",
            "file_size": str(file_size),
            "Content-Type": "application/octet-stream"
        }
        
        with open(video_path, "rb") as f:
            upload_res = requests.post(upload_url, headers=upload_headers, data=f)
        
        if upload_res.status_code != 200:
            print(f"[-] Facebook binary upload failed: {upload_res.text}")
            return

        # Step 3: Finish
        print(f"[*] Finalizing Facebook Reel publication with title: {title}...")
        finish_payload = {
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "title": title,
            "description": caption
        }
        final_res = requests.post(url, headers=headers, data=finish_payload).json()
        print(f"[+] Facebook Response: {final_res}")

    except Exception as e:
        print(f"[-] Error during Facebook upload: {e}")

def publish_facebook_photo(photo_path, caption, page_id=None):
    """
    Publishes a photo/editorial card directly to a Facebook Page.
    """
    target_page_id = (page_id or FB_PAGE_ID or "").strip()
    if not target_page_id:
        print("[!] Target Facebook Page ID missing. Skipping Facebook photo upload.")
        return None

    page_token = get_page_access_token(target_page_id)
    url = f"{BASE_URL}/{API_VERSION}/{target_page_id}/photos"
    
    try:
        with open(photo_path, "rb") as f:
            files = {"source": f}
            data = {
                "message": caption,
                "access_token": page_token
            }
            res = requests.post(url, files=files, data=data).json()
            if "id" in res:
                print(f"[+] Successfully published Facebook Photo! Post ID: {res['id']}")
                return res["id"]
            else:
                print(f"[-] Facebook photo publish failed: {res}")
                return None
    except Exception as e:
        print(f"[-] Exception publishing Facebook Photo: {e}")
        return None

def publish_threads_post(video_url, text, topic_tag=None):
    """
    Publishes a Video/Reel to Threads with optional topic_tag.
    
    Important: Threads requires a direct, publicly accessible video URL.
    GitHub raw URLs use redirects — we resolve them to the final CDN URL
    before passing to the Threads API to avoid UNKNOWN errors.
    """
    if not THREADS_USER_ID:
        print("[!] THREADS_USER_ID missing. Skipping Threads.")
        return

    # Use the specific THREAD_TOKEN if provided, otherwise fallback to ACCESS_TOKEN
    current_token = THREAD_TOKEN or ACCESS_TOKEN
    if not current_token:
        print("[!] No token found for Threads. Skipping.")
        return

    # Resolve any redirects and wait for propagation (GitHub raw -> CDN)
    resolved_url = resolve_video_url(video_url)

    print("[*] Initializing Threads container...")
    # Threads API often uses v1.0 regardless of the Graph API version
    threads_api_version = "v1.0"
    # Using 'me' is more reliable than a numeric ID which might be wrong
    url = f"{THREADS_BASE_URL}/{threads_api_version}/me/threads"
    
    # Try passing token in params as some Threads endpoints are picky
    params = {
        "access_token": current_token
    }
    # Threads has a strict 500 character limit for the 'text' parameter
    safe_text = (text or "")[:500]
    
    payload = {
        "media_type": "VIDEO",
        "video_url": resolved_url,  # Use resolved CDN URL, not the redirect
        "text": safe_text
    }
    
    # Add topic tag if provided
    if topic_tag:
        payload["topic_tag"] = topic_tag

    response = requests.post(url, params=params, data=payload).json()
    container_id = response.get("id")
    
    if not container_id:
        print(f"[-] Failed to create Threads container: {response}")
        err = response.get("error", {})
        if err.get("code") == 190:
            print("[TIP] Ensure your THREAD_TOKEN was generated specifically for Threads with 'threads_content_publish' permission.")
            print("[DEBUG] Your token prefix:", current_token[:10] if current_token else "None")
        elif "UNKNOWN" in str(response):
            print("[TIP] UNKNOWN error usually means the video URL is unreachable by Threads.")
            print(f"[TIP] Verify the URL is publicly accessible: {resolved_url}")
        return

    if check_status(container_id, "threads", token=current_token):
        print("[*] Publishing Threads post...")
        publish_url = f"{THREADS_BASE_URL}/{threads_api_version}/me/threads_publish"
        publish_payload = {
            "creation_id": container_id,
            "access_token": current_token
        }
        res = requests.post(publish_url, data=publish_payload).json()
        print(f"[+] Threads Response: {res}")

def main():
    # --- Configuration ---
    video_url_raw = "https://github.com/hamid-raza-g/holy-quran/raw/refs/heads/main/quran_273005.mp4"
    
    # Beautiful Quran Caption
    caption_text = "📖 Heart-soothing recitation from the Holy Quran. Let the words of Allah bring peace to your soul. ✨"
    hashtags = "#Quran #Islam #Peace #Spiritual #QuranRecitation #Muslim"
    full_caption = f"{caption_text}\n.\n.\n{hashtags}"
    
    # Threads specific topic (No # sign, no periods, max 50 chars)
    threads_topic = "Islam" 
    
    # --- Execution ---
    # Resolve URL first to avoid redirect issues (critical for Instagram)
    video_url = resolve_video_url(video_url_raw)
    
    # Download for Facebook if needed (Facebook Reels API via binary upload needs local file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        print(f"[*] Downloading video for Facebook Reel test...")
        tmp.write(requests.get(video_url).content)
        temp_video_path = tmp.name

    try:
        print(f"\n--- Publishing to Instagram ---")
        publish_instagram_reel(video_url, full_caption)
        
        print(f"\n--- Publishing to Facebook Page ---")
        publish_facebook_reel(temp_video_path, full_caption, title="Quran Reflection Test")
        
        print(f"\n--- Publishing to Threads ---")
        publish_threads_post(video_url, full_caption, topic_tag=threads_topic)
    finally:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

if __name__ == "__main__":
    main()
