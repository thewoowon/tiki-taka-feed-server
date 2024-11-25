import os
import requests


def rebuild_front_end():
    # 환경 변수에서 Vercel Deploy Hook URL 가져오기
    vercel_deploy_hook = os.getenv("VERCEL_DEPLOY_HOOK_URL")

    if not vercel_deploy_hook:
        raise ValueError(
            "Vercel Deploy Hook URL이 환경 변수에 설정되지 않았습니다.")

    try:
        response = requests.post(vercel_deploy_hook)
        if response.status_code != 200:
            print(f"배포 실패: {response.status_code}: {response.text}")
            return False

        print(f"배포 트리거 결과: {response.json()}")
        return True

    except requests.RequestException as e:
        print(f"배포 요청 중 에러가 발생했습니다: {e}")
        return False
