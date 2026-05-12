# README

**Name:** KYAL SIN LIN LETT **ID:** 126112

## Images

![Sample Image](screenshots/image.png)

## Hints

**Angular**

1. Backend API endpoints, middleware, models

API Endpoints:

- To add a new endpoint, if /users exists, add a new router.action method in the
  routes/users.js
- /students/getAll. Make a new routes file . Go to app.js, make a new
  studentRouter, and add app.use

Middleware:

- The middleware, auth.js, It has req, res, next.. If you call next() method in
  your middleware, it triggers the code in actual router.method
- If you want to protect your endpoint from unauthenticated access, add
  middlware. The format is router.method('/smth', middleware(), function)

Models:

- Add a new model, schema...

Angular:

- Localstorage
- Login/Register/Logout
- \*ngIf
- Component creation and adding a route to it, ng g c ComponentName...
- To add a route, go to app.routes.ts, inside routes array, add { route: 'chat',
  component: ChatComponent, canActivate: [middleware]}
- Unit Testing

React:

- Localstorage
- Login/Register/Logout
- useState, useEffect
- To add a route, inside <Routes><Route path='' element={Component}>
  </Route></Routes>
- To protect your frontend page, use the react hook, useEffect
- To redirect, add a link , use <Link to='/login'>

Frontend:

- conditional rendering (\*ngIf, ternary, &&)
