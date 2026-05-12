var express = require('express');
var router = express.Router();
var User = require('../models/user')
const jwt = require('jsonwebtoken');
const verifyToken = require('../middleware/auth')

const SECRET_KEY = 'jwtsecretkey'

router.post('/login', async function (req, res, next) {
  const { email, password } = req.body;

  const existing_user = await User.findOne({ email })

  if (!existing_user) {
    return res.status(400).json({ message: "User not found" })
  }

  const isMatch = await existing_user.comparePassword(password);
  if (!isMatch) return res.status(401).json({ message: "Invalid email or password" });

  const token = jwt.sign({ email }, SECRET_KEY, { expiresIn: '1h' })
  res.status(200).json({ token: token, user: existing_user })
})

router.post('/register', async function (req, res, next) {
  const { email, password } = req.body;

  if (!email || !password) {
    res.status(400).json({ message: "Empty fields!" })
  }

  const existing_user = await User.findOne({ email })

  if (existing_user) {
    return res.status(400).json({ message: "Email already in use." })
  }

  const new_user = new User({ email, password })
  await new_user.save()

  res.status(200).json({ new_user })
})

module.exports = router;
