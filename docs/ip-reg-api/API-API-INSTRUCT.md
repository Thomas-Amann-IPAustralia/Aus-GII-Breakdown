# APIs at IP Australia

## What are APIs?

An application programming interface (API) is, in its simplest terms, a piece of software which is designed to fulfil a particular function, provides a clear and fixed contract which other software can use to interact with it, and has a standard address or *endpoint* where its implementation can be found. It is, for all intents and purposes, a user interface for machines.

One analogy for an API is the simple act of going to a coffee shop to purchase a coffee - in this case, the barista can be likened to an API. First you need to go to where they are located - the coffee shop or, in this analogy, the API *endpoint*. Next you need to fulfil the general contract: tell the barista which of their services you want to use: make a coffee, provide further details as required: an espresso, and provide payment. Finally, the barista will perform some actions and fulfil their end of the contract returning you a nice cup of coffee. It's important to note here that as a consumer of their services you do not actually need to know anything about the actions they perform - the details of *how* they fulfil the contract are not important to you, the consumer, it is the contract that is important.

## APIs at IP Australia

IP Australia follows the defacto web standard by exposing APIs as [RESTful web services](https://en.wikipedia.org/wiki/Representational_state_transfer), allowing interchange of data using standard internet protocols and data structures that are independent of underlying technologies so that they can be utilised by all customers regardless of their programming language of choice or physical location.

Each API is documented on our [API Exchange Portal](https://anypoint.mulesoft.com/exchange/portals/ip-australia-3/), where you will find details of the operations they provide and any other specific information needed to understand or invoke them. In addition to this, the API contract can be downloaded in [RAML](https://raml.org/) format - an API modelling language that is designed to be both machine and human readable.

## What languages can I use to invoke an API?

The APIs exposed by IP Australia are intended to follow open standards and be language and platform agnostic. Any system capable of forming a [JSON](https://www.json.org/) string and issuing an HTTP request can be used to invoke a RESTful API. It is specifically important to note that you do not need to use the same technologies that IP Australia uses internally.

## Can I get a client for an API in my language of choice?

Some developers prefer to generate an API client rather than crafting the JSON payload and issuing HTTP requests themselves. These clients usually take the form of generated source code in the consumers language of choice and provide a simpler mechanism of invoking the API without the need to build their own validation and/or data transformation mechanisms.

While IP Australia does not provide such clients, the machine readable nature of the RAML descriptor means that there are client generators available for many programming languages - see the [RAML.org projects](https://raml.org/projects) page for examples.

Please note that IP Australia has not tested and does not provide endorsement for any such third party projects. You should consider each project on its own merits before deciding to utilise them.

## Example API and Invocations

Consider the following API which provides a single method to send a message to a user.

```yaml
#%RAML 1.0
title: Messaging API
description: API for sending messages
baseUri: https://example.com/api
mediaType: application/json

/messages:
  post:
    description: Sends a short message to a user
    body:
      properties:
        recipient: string
        sender: string
        message: string
    responses:
      202:
        description: |
          Accepted - message has been queued for sending.
      400:
        description: |
          Bad Request - the message body does not meet the requirements
          of the API.
```

The following sections show examples of invoking the send message API using differing technologies.

## curl
```curl
curl -X POST \
  https://example.com/api/messages \
  -H 'Content-Type: application/json' \
  -d '{ "recipient": "Fred", "sender": "Barney", "message": "Hi Fred" }'

## Java (OkHttp)
OkHttpClient client = new OkHttpClient();

MediaType mediaType = MediaType.parse("application/json");

RequestBody body = RequestBody.create(
    mediaType,
    "{\n\t\"recipient\": \"Fred\",\n\t\"sender\": \"Barney\",\n\t\"message\": \"Hi Fred\"\n}"
);

Request request = new Request.Builder()
    .url("https://example.com/api/messages")
    .post(body)
    .addHeader("Content-Type", "application/json")
    .build();

Response response = client.newCall(request).execute();
```
## C# (RestSharp)
```C#
var client = new RestClient("https://example.com/api/messages");
var request = new RestRequest(Method.POST);

request.AddHeader("Content-Type", "application/json");

request.AddParameter(
    "undefined",
    "{\n\t\"recipient\": \"Fred\",\n\t\"sender\": \"Barney\",\n\t\"message\": \"Hi Fred\"\n}",
    ParameterType.RequestBody
);

IRestResponse response = client.Execute(request);

## PHP (HttpRequest)
```php
<?php

$request = new HttpRequest();

$request->setUrl('https://example.com/api/messages');
$request->setMethod(HTTP_METH_POST);

$request->setHeaders(array(
    'Content-Type' => 'application/json'
));

$request->setBody('{
    "recipient": "Fred",
    "sender": "Barney",
    "message": "Hi Fred"
}');

try {
    $response = $request->send();
    echo $response->getBody();
} catch (HttpException $ex) {
    echo $ex;
}
```

## JavaScript (jQuery)
```JavaScript
var settings = {
    "async": true,
    "crossDomain": true,
    "url": "https://example.com/api/messages",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json"
    },
    "processData": false,
    "data": "{\n\t\"recipient\": \"Fred\",\n\t\"sender\": \"Barney\",\n\t\"message\": \"Hi Fred\"\n}"
};

$.ajax(settings).done(function (response) {
    console.log(response);
});

## Go
package main

import (
    "fmt"
    "strings"
    "net/http"
    "io/ioutil"
)

func main() {
    url := "https://example.com/api/messages"

    payload := strings.NewReader(
        "{\n\t\"recipient\": \"Fred\",\n\t\"sender\": \"Barney\",\n\t\"message\": \"Hi Fred\"\n}",
    )

    req, _ := http.NewRequest("POST", url, payload)

    req.Header.Add("Content-Type", "application/json")

    res, _ := http.DefaultClient.Do(req)

    defer res.Body.Close()

    body, _ := ioutil.ReadAll(res.Body)

    fmt.Println(res)
    fmt.Println(string(body))
}

## Raw HTTP
POST /api/messages HTTP/1.1
Host: example.com
Content-Type: application/json

{
    "recipient": "Fred",
    "sender": "Barney",
    "message": "Hi Fred"
}
