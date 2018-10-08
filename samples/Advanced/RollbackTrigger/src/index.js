'use strict';

const AWS = require('aws-sdk');

const createResponse = (statusCode, body) => ({ statusCode, body });

exports.get = (event, context, callback) => {

    console.log(event.pathParameters.name);
    callback(null, createResponse(200, `Hello world: ${event.pathParameters.name}!`));

};
