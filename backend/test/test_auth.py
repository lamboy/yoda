import requests
from lib.util import generate_string
from lib.authentication import login_header, token_header
from util import uri


# --------------------------------------------------------------------------------------------------------------------
def test_root():

    response = requests.get(uri('auth'))
    assert response.status_code == 200


# --------------------------------------------------------------------------------------------------------------------
def test_request_token():

    response = requests.post(uri('auth', '/tokens'), headers=login_header('ralph', 'secret'))
    assert response.status_code == 201
    assert response.json()['token']
    response = requests.post(uri('auth', '/tokens'), headers=login_header('x', 'xxx'))
    assert response.status_code == 403


# --------------------------------------------------------------------------------------------------------------------
def test_check_token():

    response = requests.post(uri('auth', '/tokens'), headers=login_header('ralph', 'secret'))
    assert response.status_code == 201
    token1 = response.json()['token']
    response = requests.post(uri('auth', '/tokens'), headers=login_header('quentin', 'secret'))
    assert response.status_code == 201
    token2 = response.json()['token']
    assert token1 != token2
    response = requests.post(uri('auth', '/token-checks'), json={'token': token2}, headers=token_header(token1))
    assert response.status_code == 201
    response = requests.post(uri('auth', '/token-checks'), headers=token_header('1234'))
    assert response.status_code == 403


# --------------------------------------------------------------------------------------------------------------------
def test_users():

    response = requests.post(uri('auth', '/tokens'), headers=login_header('ralph', 'secret'))
    assert response.status_code == 201
    token = response.json()['token']
    response = requests.get(uri('auth', '/users'), headers=token_header(token))
    assert response.status_code == 200
    assert len(response.json()) >= 4


# --------------------------------------------------------------------------------------------------------------------
def test_create_update_and_delete_user():

    response = requests.post(uri('auth', '/tokens'), headers=login_header('ralph', 'secret'))
    assert response.status_code == 201
    token = response.json()['token']
    data = {
        'username': generate_string(),
        'password': 'secret',
        'email': '{}@yoda.com'.format(generate_string()),
    }

    # Create user
    response = requests.post(uri('auth', '/users'), json=data, headers=token_header(token))
    assert response.status_code == 201
    user_id = response.json()['id']

    # Update user and check update was successful
    data['first_name'] = 'John'
    response = requests.put(uri('auth', '/users/{}'.format(user_id)), json=data, headers=token_header(token))
    assert response.status_code == 200
    response = requests.get(uri('auth', '/users/{}'.format(user_id)), headers=token_header(token))
    assert response.status_code == 200
    assert response.json()['first_name'] == 'John'

    # Delete user and check it no longer exists
    response = requests.delete(uri('auth', '/users/{}'.format(user_id)), headers=token_header(token))
    assert response.status_code == 204
    response = requests.get(uri('auth', '/users/{}'.format(user_id)), headers=token_header(token))
    assert response.status_code == 404


# --------------------------------------------------------------------------------------------------------------------
def test_create_update_and_delete_group():

    response = requests.post(uri('auth', '/tokens'), headers=login_header('ralph', 'secret'))
    assert response.status_code == 201
    token = response.json()['token']
    data = {'name': generate_string()}

    # Create group
    response = requests.post(uri('auth', '/user-groups'), json=data, headers=token_header(token))
    assert response.status_code == 201
    user_group_id = response.json()['id']

    # Update group and check update successful
    data['name'] = generate_string()
    response = requests.put(uri('auth', '/user-groups/{}'.format(user_group_id)), json=data, headers=token_header(token))
    assert response.status_code == 200
    response = requests.get(uri('auth', '/user-groups/{}'.format(user_group_id)), headers=token_header(token))
    assert response.status_code == 200
    assert response.json()['name'] == data['name']

    # Add user to group and check it was added
    response = requests.get(uri('auth', '/users?username=ralph'), headers=token_header(token))
    assert response.status_code == 200
    user_id = response.json()[0]['id']
    response = requests.put(uri('auth', '/user-groups/{}/users/{}'.format(user_group_id, user_id)), headers=token_header(token))
    assert response.status_code == 200
    response = requests.get(uri('auth', '/user-groups/{}/users'.format(user_group_id)), headers=token_header(token))
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['username'] == 'ralph'

    # Remove user from group and check it was successfully removed
    response = requests.delete(uri('auth', '/user-groups/{}/users/{}'.format(user_group_id, user_id)), headers=token_header(token))
    assert response.status_code == 200
    response = requests.get(uri('auth', '/user-groups/{}/users'.format(user_group_id)), headers=token_header(token))
    assert response.status_code == 200
    assert len(response.json()) == 0

    # Delete group and check it no longer exists
    response = requests.delete(uri('auth', '/user-groups/{}'.format(user_group_id)), headers=token_header(token))
    assert response.status_code == 204
    response = requests.get(uri('auth', '/user-groups/{}'.format(user_group_id)), headers=token_header(token))
    assert response.status_code == 404
