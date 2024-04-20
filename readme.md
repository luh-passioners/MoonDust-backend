# backend

1. `python -m venv env`
2. `./env/Scripts/Activate` or whatever MEOW
3. `pip install -r requirements.txt`!

## keys.py

```python
MONGO_USER = "[...]"
MONGO_PASS = "[...]"
JWT_KEY = "[...]"
```

## notes

username is just email

## db

collection `users`:
- username
- name
- hashed
- company
- type (full or org)
- org_id? (if type == full)

collection `transaction`:
- name
- company
- org_id
- date
- amount

collections `orgs`:
- company
- name