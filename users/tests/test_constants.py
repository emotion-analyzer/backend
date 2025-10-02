valid_user_1 = {
    "password": "jorgito_pw",
    "username": "jorgito",
    "email": "jorgito@gmail.com",
}

valid_user_2 = {
    "password": "pepe_pw",
    "username": "pepe",
    "email": "pepe@gmail.com",
}

valid_user_3 = {
    "password": "miguel_pw",
    "username": "miguel",
    "email": "miguel@gmail.com",
}

repeated_email_user_1 = {
    "password": "jorge_pw",
    "username": "jorge",
    "email": "jorgito@gmail.com",
}

user_1_details_update = {
    "username": "camilo",
}

user_1_email_update_wrong_pw = {
    "email": "camilo@gmail.com",
    "current_password": "invalid_pw"
}

user_1_email_update = {
    "email": "camilo@gmail.com",
    "current_password": "jorgito_pw"
}

user_1_pw_update_mismatch = {
    "current_password": "jorgelin_pw",
    "new_password": "camilo_pw",
}

user_1_pw_update = {
    "current_password": "jorgito_pw",
    "new_password": "camilo_pw",
}

user_1_updated_login = {
    "email": "jorgito@gmail.com",
    "password": "camilo_pw"
}

invalid_password_reset = {
    "token": "invalid_token",
    "new_password": "jorgito_new_pw"
}

invalid_user = {"password": "anita_pw",
                "username": "anita"}
