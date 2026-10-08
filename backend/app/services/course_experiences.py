from fastapi import HTTPException, status

EXPERIENCES = {}


def validate_experience_key(key: str) -> str:
    if key == "unlinked":
        return key
    if key not in EXPERIENCES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="课程模块未注册")
    return key
