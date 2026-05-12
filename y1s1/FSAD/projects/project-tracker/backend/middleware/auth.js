const jwt = require('jsonwebtoken')

module.exports = function (headerName) {
  return function (req, res, next) {
    const authHeader = req.headers['authorization']
    console.log(authHeader)

    if (!authHeader) {
      res.status(400).json({
        error: `Missing required header: ${headerName}`
      });
    }

    const token = authHeader.split(" ")[1];

    jwt.verify(token, "jwtsecretkey", (err, dec) => {
      if (err) {
        res.status(401).json({ error: 'Invalid token' })
      }
      next();
    })
  };
};
