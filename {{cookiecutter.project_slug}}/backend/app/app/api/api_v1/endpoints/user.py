from fastapi.encoders import jsonable_encoder
from flask import abort
from flask_apispec import doc, marshal_with, use_kwargs
from flask_jwt_extended import get_current_user, jwt_required
from webargs import fields

from app.api.api_v1.api_docs import docs, security_params
from app.core import config
from app.crud.user import (
    check_if_user_is_active,
    check_if_user_is_superuser,
    get_user,
    get_users,
    search_users,
    update_user,
    upsert_user,
)
from app.db.database import get_default_bucket
from app.main import app
from app.models.user import UserInCreate, UserInUpdate
from app.schemas.user import UserSchema
from app.utils import send_new_account_email


@docs.register
@doc(description="Retrieve users", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/", methods=["GET"])
@use_kwargs(
    {"skip": fields.Int(default=0), "limit": fields.Int(default=100)},
    locations=["query"],
)
@marshal_with(UserSchema(many=True))
@jwt_required
def route_users_get(skip=0, limit=100):
    current_user = get_current_user()
    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not check_if_user_is_superuser(current_user):
        abort(400, "The user doesn't have enough privileges")
    bucket = get_default_bucket()
    users = get_users(bucket, skip=skip, limit=limit)
    return users


@docs.register
@doc(description="Search users", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/search/", methods=["GET"])
@use_kwargs(
    {
        "q": fields.Str(required=True),
        "skip": fields.Int(default=0),
        "limit": fields.Int(default=100),
    },
    locations=["query"],
)
@marshal_with(UserSchema(many=True))
@jwt_required
def route_users_search_get(q, skip=0, limit=100):
    current_user = get_current_user()
    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not check_if_user_is_superuser(current_user):
        abort(400, "The user doesn't have enough privileges")
    bucket = get_default_bucket()
    users = search_users(bucket=bucket, query_string=q, skip=skip, limit=limit)
    return users


@docs.register
@doc(description="Create new user", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/", methods=["POST"])
@use_kwargs(
    {
        "username": fields.Str(required=True),
        "password": fields.Str(required=True),
        "admin_channels": fields.List(fields.Str()),
        "admin_roles": fields.List(fields.Str()),
        "disabled": fields.Boolean(),
        "email": fields.Str(),
        "full_name": fields.Str(),
    }
)
@marshal_with(UserSchema())
@jwt_required
def route_users_post(
    *,
    username,
    password,
    admin_channels=[],
    admin_roles=[],
    disabled=False,
    email=None,
    full_name=None,
):
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not check_if_user_is_superuser(current_user):
        abort(400, "The user doesn't have enough privileges")
    bucket = get_default_bucket()
    user = get_user(bucket, username)
    if user:
        return abort(400, f"The user with this username already exists in the system.")
    user_in = UserInCreate(
        username=username,
        password=password,
        admin_channels=admin_channels,
        admin_roles=admin_roles,
        disabled=disabled,
        email=email,
        full_name=full_name,
    )
    user = upsert_user(bucket, user_in)
    if config.EMAILS_ENABLED:
        send_new_account_email(email_to=email, username=username, password=password)
    return user


@docs.register
@doc(description="Update a user", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/<username>", methods=["PUT"])
@use_kwargs(
    {
        "password": fields.Str(),
        "admin_channels": fields.List(fields.Str()),
        "admin_roles": fields.List(fields.Str()),
        "disabled": fields.Boolean(),
        "email": fields.Str(),
        "full_name": fields.Str(),
    }
)
@marshal_with(UserSchema())
@jwt_required
def route_users_put(
    *,
    username,
    password=None,
    admin_channels=None,
    admin_roles=None,
    disabled=None,
    email=None,
    full_name=None,
):
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not check_if_user_is_superuser(current_user):
        abort(400, "The user doesn't have enough privileges")
    bucket = get_default_bucket()
    user = get_user(bucket, username)

    if not user:
        return abort(404, f"The user with this username does not exist in the system.")
    user_in = UserInUpdate(
        username=username,
        password=password,
        admin_channels=admin_channels,
        admin_roles=admin_roles,
        disabled=disabled,
        email=email,
        full_name=full_name,
    )
    user = update_user(bucket, user_in)
    return user


@docs.register
@doc(description="Update own user", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/me", methods=["PUT"])
@use_kwargs(
    {"password": fields.Str(), "full_name": fields.Str(), "email": fields.Str()}
)
@marshal_with(UserSchema())
@jwt_required
def route_users_me_put(*, password=None, full_name=None, email=None):
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    user_in = UserInUpdate(jsonable_encoder(current_user))
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    bucket = get_default_bucket()
    user = update_user(bucket, user_in)
    return user


@docs.register
@doc(description="Get current user", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/me", methods=["GET"])
@marshal_with(UserSchema())
@jwt_required
def route_users_me_get():
    current_user = get_current_user()
    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    return current_user


@docs.register
@doc(
    description="Get a specific user by username (email)",
    security=security_params,
    tags=["users"],
)
@app.route(f"{config.API_V1_STR}/users/<username>", methods=["GET"])
@marshal_with(UserSchema())
@jwt_required
def route_users_id_get(username):
    current_user = get_current_user()  # type: User
    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    bucket = get_default_bucket()
    user = get_user(bucket, username)
    if user == current_user:
        return user
    if not check_if_user_is_superuser(current_user):
        abort(400, "The user doesn't have enough privileges")
    return user


@docs.register
@doc(description="Create new user without the need to be logged in", tags=["users"])
@app.route(f"{config.API_V1_STR}/users/open", methods=["POST"])
@use_kwargs(
    {
        "username": fields.Str(required=True),
        "password": fields.Str(required=True),
        "email": fields.Str(),
        "full_name": fields.Str(),
    }
)
@marshal_with(UserSchema())
def route_users_post_open(*, username, password, email=None, full_name=None):
    if not config.USERS_OPEN_REGISTRATION:
        abort(403, "Open user resgistration is forbidden on this server")
    bucket = get_default_bucket()
    user = get_user(bucket, username)
    if user:
        return abort(400, f"The user with this username already exists in the system")
    user_in = UserInCreate(
        username=username, password=password, email=email, full_name=full_name
    )
    user = upsert_user(bucket, user_in)
    return user
