curl -i -H "Content-Type: application/json" -X 'POST' `
    -d '{ \"name\": \"Group 1\" \"images\": [\"title\": \"Bit1\", \"id\": 33, \"imagefilepath\": \"path1\"]}' `
    'http://localhost:5000/groups/new'

curl -i -H "Content-Type: application/json" -X 'PUT' `
    -d '{  \"id\": 1, \"name\": \"Group 1\" \"images\": [\"title\": \"Bit1\", \"id\": 33, \"imagefilepath\": \"path1\"]}' `
    'http://localhost:5000/groups/new'