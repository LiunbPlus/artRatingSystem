from app.repositories import user_repository


def login(username: str, password: str):
    return user_repository.verify(username, password)


def register(username: str, password: str, invite_code: str) -> tuple:
    if len(username) < 2:
        return False, "用户名至少2个字符", None
    if not (password.isdigit() and len(password) == 4):
        return False, "密码必须为4位纯数字", None
    return user_repository.create(username, password, invite_code)


def change_password(user: dict, old_password: str, new_password: str) -> tuple[bool, str]:
    if user["role"] == "judge":
        if not (new_password.isdigit() and len(new_password) == 4):
            return False, "新密码必须为4位纯数字"
    elif len(new_password) < 6:
        return False, "新密码至少6个字符"
    return user_repository.change_password(user["id"], old_password, new_password)
