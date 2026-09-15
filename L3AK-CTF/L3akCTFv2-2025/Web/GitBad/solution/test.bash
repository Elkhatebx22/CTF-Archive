git submodule update --init --recursive 
cat /var/log/supervisor/flask.log

# { filter: { $facet: { flag: [ { $unionWith: "config" } ] } } }
curl "http://localhost/api/search?debug=true&filter=%7B%22%24facet%22%3A%7B%22flag%22%3A%5B%7B%22%24unionWith%22%3A%22config%22%7D%5D%7D%7D"
curl "http://127.0.0.1/api/search.js?debug=true&filter=%7B%22%24facet%22%3A%7B%22flag%22%3A%5B%7B%22%24unionWith%22%3A%22config%22%7D%5D%7D%7D"
