<?php
$directory = "./files";
$secret = 'faaaakee';
$message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['newfile'])) {

    if ($_FILES['newfile']['error'] === UPLOAD_ERR_OK) {

        $original_filename = basename($_FILES['newfile']['name']);
        $file_extension = strtolower(pathinfo($original_filename, PATHINFO_EXTENSION));

        if ($file_extension !== 'txt') {
            $message = "<p class='error-message'>Error: Only .txt files are allowed.</p>";
        } else {

            $allowed_algos = ['md4', 'md5', 'ripemd160', 'sha1', 'sha256', 'sha512', 'whirlpool'];
            $upload_algo = 'md5';


            if (isset($_POST['upload_algo']) && in_array($_POST['upload_algo'], $allowed_algos, true)) {
                $upload_algo = $_POST['upload_algo'];
            }

            $destination = $directory . '/' . $original_filename;

            if (move_uploaded_file($_FILES['newfile']['tmp_name'], $destination)) {
                $hash = hash($upload_algo, $secret . $original_filename);
                $view_link = "index.php?algo=$upload_algo&file=" . urlencode($original_filename) . "&hash=$hash";

                $message = "<p class='success-message'>File '<strong>" . htmlspecialchars($original_filename) . "</strong>' uploaded. <a href='$view_link'>View your file</a>.</p>";

            } else {
                $message = "<p class='error-message'>Error: Could not save the uploaded file. Check directory permissions.</p>";
            }
        }
    } else {
        $message = "<p class='error-message'>An error occurred during upload. Please try again.</p>";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Upload a New File</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root {
    --bg-color: #f4f7f9;
    --text-color: #333;
    --accent-color: #007bff;
    --accent-hover: #0056b3;
    --border-color: #dee2e6;
    --card-bg: #ffffff;
    --success-color: #28a745;
    --error-color: #d9534f;
}
body { margin: 0; font-family: 'Inter', sans-serif; background-color: var(--bg-color); color: var(--text-color); display: flex; align-items: center; justify-content: center; min-height: 100vh; }
.upload-container { background: var(--card-bg); padding: 2.5rem; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 100%; max-width: 500px; }
h1 { margin-top: 0; text-align: center; border-bottom: 2px solid var(--border-color); padding-bottom: 1rem; }
.upload-form label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.upload-form select, .upload-form input[type="file"], .upload-form input[type="submit"] { width: 100%; padding: 0.75rem; margin-bottom: 1rem; border-radius: 5px; border: 1px solid var(--border-color); font-size: 1rem; box-sizing: border-box; }
.upload-form input[type="submit"] { background-color: var(--accent-color); color: white; border: none; cursor: pointer; font-weight: bold; transition: background-color 0.2s; }
.upload-form input[type="submit"]:hover { background-color: var(--accent-hover); }
.message-area { margin-top: 1.5rem; text-align: center; font-size: 1.1rem; }
.error-message { color: var(--error-color); font-weight: bold; }
.success-message { color: var(--success-color); font-weight: bold; }
.success-message a, .nav-link a { color: var(--accent-hover); }
.nav-link { display: block; text-align: center; margin-top: 1.5rem; }
</style>
</head>
<body>
<div class="upload-container">
<h1>Upload a New File</h1>

<form class="upload-form" action="upload.php" method="POST" enctype="multipart/form-data">
<label for="newfile">Select .txt file:</label>
<input type="file" name="newfile" id="newfile" required accept=".txt">

<label for="upload_algo">Hash with algorithm:</label>
<select name="upload_algo" id="upload_algo">
<option value="md4">md4</option>
<option value="md5">md5</option>
<option value="ripemd160">ripemd160</option>
<option value="sha1">sha1</option>
<option value="sha256">sha256</option>
<option value="sha512">sha512</option>
<option value="whirlpool">whirlpool</option>
</select>

<input type="submit" value="Upload and Process File">
</form>

<?php if (!empty($message)): ?>
<div class="message-area">
<?php echo $message; ?>
</div>
<?php endif; ?>

<div class="nav-link">
<a href="index.php">Back to File Viewer</a>
</div>
</div>
</body>
</html>
