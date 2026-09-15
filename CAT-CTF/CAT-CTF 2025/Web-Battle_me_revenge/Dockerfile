FROM php:8.2-apache

WORKDIR /var/www/html

COPY index.php .
COPY upload.php .
COPY flag.txt /tmp/flag.txt
COPY files/ ./files/

RUN chown -R www-data:www-data /var/www/html/files
