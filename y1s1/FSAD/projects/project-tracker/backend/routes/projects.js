var express = require('express');
var router = express.Router();
var Project = require('../models/project')
var authMiddleware = require("../middleware/auth")();

function getRandomNumber(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

/* GET. */
router.get('/', authMiddleware, async function (req, res, next) {

    let projects = await Project.find()

    if (projects.length === 0) {
        projects = [
            { id: 1, name: 'Water Mgmt' },
            { id: 2, name: 'CLeaning' },
            { id: 3, name: 'CLeaning 1' },
            { id: 4, name: 'CLeaning 2' },
            { id: 5, name: 'CLeaning 3' },
        ]
    }

    res.send(projects);
});

/* GET. */
router.get('/random', async function (req, res, next) {
    let projects = await Project.find()

    if (projects.length === 0) {
        projects = [
            { id: 1, name: 'Water Mgmt' },
            { id: 2, name: 'CLeaning' },
            { id: 3, name: 'CLeaning 1' },
            { id: 4, name: 'CLeaning 2' },
            { id: 5, name: 'CLeaning 3' },
        ]
    }

    const project = projects[Math.floor(Math.random() * projects.length)];

    res.send(project);
});

/* GET. */
router.get('/:id', authMiddleware, async function (req, res, next) {
    const { id } = req.params;
    console.log(id)
    let projects = await Project.find()

    if (projects.length === 0) {
        projects = [
            { id: 1, name: 'Water Mgmt' },
            { id: 2, name: 'CLeaning' },
            { id: 3, name: 'CLeaning 1' },
            { id: 4, name: 'CLeaning 2' },
            { id: 5, name: 'CLeaning 3' },
        ]
    }

    const project = projects.find(p => p.id == id);

    res.send(project);
});

module.exports = router;
