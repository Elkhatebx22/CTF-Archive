<?php

$directory = "./files";
$algo = 'md5';
$title = '';
$secret = 'fake';

$allowed_algos = ['md4', 'md5', 'ripemd160', 'sha1', 'sha256', 'sha512', 'whirlpool'];
if (isset($_GET['algo']) && is_string($_GET['algo']) && in_array($_GET['algo'], $allowed_algos, true)) {
    $algo = $_GET['algo'];
} else {
    $algo = 'md5';
}

if (isset($_GET['file']) and isset($_GET['hash'])) {
    if (hash($algo, $secret . $_GET['file']) == $_GET['hash']) {
        $fileToGet = $directory . "/" . $_GET['file'];
        $fileToGet = str_replace("\0", '', $fileToGet);
        $theData = nl2br(file_get_contents($fileToGet));
        $title = $_GET['file'];
    } else {
        header($_SERVER["SERVER_PROTOCOL"] . " 404 Not Found");
        $title = "File not found";
        $header = $title;
        $theData = "<p class='error-message'>Invalid hash or file not found.</p>";
    }
} else {
    $theData = "Please select an option from the left.";
    $title = "Home"; 
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Battle_Me<?php print $title; ?></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #f4f7f9;
            --sidebar-bg: #1a1d24;
            --text-color: #333;
            --sidebar-text: #e0e0e0;
            --accent-color: #007bff;
            --accent-hover: #0056b3;
            --border-color: #dee2e6;
            --card-bg: #ffffff;
        }

        body { margin: 0; font-family: 'Inter', sans-serif; background-color: var(--bg-color); color: var(--text-color); display: flex; height: 100vh; overflow: hidden; }
        #sidebar { width: 280px; background: var(--sidebar-bg); color: var(--sidebar-text); padding: 1.5rem; display: flex; flex-direction: column; border-right: 1px solid var(--border-color); }
        #sidebar h2 { margin: 0 0 1rem 0; font-size: 1.5rem; text-align: center; border-bottom: 1px solid #333; padding-bottom: 1rem; }
        .settings-form { margin-bottom: 1.5rem; }
        #sidebar label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
        #sidebar select, #sidebar input[type="submit"], #sidebar a.button { width: 100%; padding: 0.75rem; margin-top: 0.5rem; border-radius: 5px; border: 1px solid #444; background-color: #2c313a; color: var(--sidebar-text); font-size: 1rem; box-sizing: border-box; text-decoration: none; display: block; text-align: center; }
        #sidebar input[type="submit"], #sidebar a.button { background-color: var(--accent-color); border: none; cursor: pointer; font-weight: bold; transition: background-color 0.2s; margin-bottom: 1.5rem; }
        #sidebar input[type="submit"]:hover, #sidebar a.button:hover { background-color: var(--accent-hover); }
        #sidebar ul { list-style: none; padding: 0; margin: 0; overflow-y: auto; flex-grow: 1; }
        #sidebar li a { display: block; padding: 0.75rem 1rem; color: var(--sidebar-text); text-decoration: none; border-radius: 5px; transition: background-color 0.2s, color 0.2s; word-break: break-all; }
        #sidebar li a:hover { background-color: #2c313a; color: #fff; }
        #main-content { flex: 1; padding: 2rem; overflow-y: auto; }
        .content-card { background: var(--card-bg); padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .content-card h1 { margin-top: 0; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem; }
        .error-message { color: #d9534f; font-weight: bold; }
        @media (max-width: 768px) {
            body { flex-direction: column; }
            #sidebar { width: 100%; height: auto; border-right: none; border-bottom: 1px solid var(--border-color); }
        }
    </style>
</head>
<body>

<aside id="sidebar">
    <h2>File Menu</h2>
    
    <a href="upload.php" class="button">Upload New File</a>

    <form class="settings-form" action="<?php print $_SERVER['PHP_SELF']; ?>" method="GET">
        <label for="algo">Algorithm:</label>
        <select name="algo" id="algo">
            <option value="md4">md4</option>
            <option value="md5" <?php if ($algo === 'md5') echo 'selected'; ?>>md5</option>
            <option value="ripemd160">ripemd160</option>
            <option value="sha1">sha1</option>
            <option value="sha256">sha256</option>
            <option value="sha512">sha512</option>
            <option value="whirlpool">whirlpool</option>
        </select>
        <input type="submit" value="Save">
    </form>
    <nav>
        <ul>
            <?php
            $files = glob("./files/*");
            foreach ($files as $file) {
                if (is_file($file)) {
                    $fileName = basename($file);
                    $url = "algo=" . $algo;
                    print "<li><a href=\"?$url&file=" . $fileName . "&hash=" . hash($algo, $secret . $fileName) . "\">" . $fileName . "</a></li>";
                }
            }
            ?>
        </ul>
    </nav>
</aside>

<main id="main-content">
    <div class="content-card">
        <h1><?php print $title; ?></h1>
        <div>
            <?php print @$theData; ?>
        </div>
    </div>
</main>

</body>
</html>
