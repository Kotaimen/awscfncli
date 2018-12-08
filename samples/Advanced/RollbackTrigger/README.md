# Rollback Trigger

Uncomment "RollbackTrigger" section and update the stack to enable rollback 
trigger.

To see rollback trigger in action, change returned string (eg: `hello-world`) 
and update stack.  After 5 minutes the stack update will fail and be rolled back. 

```javascript
exports.get = (event, context, callback) => {

    console.log(event.pathParameters.name);
    callback(null, createResponse(200, `Hello world: ${event.pathParameters.name}!`));

};
```