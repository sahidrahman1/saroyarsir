#!/usr/bin/env python3
from app import create_app
import json

app = create_app()

with app.test_client() as client:
    # Pick first student who has a batch
    student_resp = client.get('/api/students')
    students = student_resp.get_json().get('data', [])
    student_id = None
    for s in students:
        if s.get('batchId'):
            student_id = s['id']
            break

    if not student_id:
        print('No enrolled students available to test fees. Aborting.')
        exit(1)

    print('Using student id:', student_id)

    payload = {'student_id': student_id, 'month': 1, 'year': 2025, 'amount': 50}
    resp = client.post('/api/fees/monthly-save', json=payload)
    print('monthly-save status:', resp.status_code)
    print('response:', resp.get_json())
