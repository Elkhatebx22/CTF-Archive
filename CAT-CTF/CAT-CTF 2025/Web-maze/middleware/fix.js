const fixUrl = (req, res, next) => {
  const extensionRegex = /\.(css|js|jpg|jpeg|png|gif|svg|ico)$/i;
  if (req.url.match(extensionRegex)) {
    req.url = req.url.replace(extensionRegex, '');
  }
  return next();
};

module.exports = fixUrl;
