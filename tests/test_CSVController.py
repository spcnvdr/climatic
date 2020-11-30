def test_upload_csv(www):
    file = "example.csv"
    data = {
        'csv_file': (open(file, 'rb'), file)
    }
    response = www.post('/upload/csv', data=data)
    assert response.status_code == 200
