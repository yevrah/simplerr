Urgent for 0.16 release
=======================

The 0.16 release aims to stabilise basic web routing and functionality, as well
as provide adequate documentation to get developers started in the world of
Simplerr Development.

## 0. Basic features still missing

[ ] Easy file upload
[ ] Easy access to request and response objects


## 1. Fix issues when errors occur

[x] 1.1 Test when not in debug mode - currently not able to disable debug mode from manage.py
[ ] 1.2 Create cusomisable error templates

## 2. Bug where by responses slow down after an error, test errors with 1 thread to replicate

Could not replicate - needs more testing

## 3. Bug in json posts

Temp work around is to json.loads(request.data)

## 4. Ensure multiple routes to the same method are possible

For example, we should be able to allow the same method to be used for multiple
routes, for example:

```python
@web('/e/<msg>')
@web('/echo/<msg>')
def echo(request, msg):
  return msg
```

## 5. Ensure methods=['GET', 'POST', 'DELETE', 'PUT', 'ANY'] are respected


For example, we should be able to request routes as per the example below.

```python
@web('/form/action', methods=['POST'])
def form_action(request):
  return request.form['var']
```

## 6. Static file sending improvements

6.1 Ensure that we can specify allowed file types when proxying files, for example:

```python
@web('/static/<path:file>', file=True, allow=['*.html', '*.js', '*.css'])
def static(request, file):
  return file
```

6.2 Review efficient file handing - streaming, and web server bypass

## 7. Egg builds and PyPy install

See example package implementations below
 - http://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/quickstart.html
 - http://veekaybee.github.io/2017/09/26/python-packaging/?utm_source=mybridge&utm_medium=blog&utm_campaign=read_more for a workflow.
 - https://milkr.io/kfei/5-common-patterns-to-version-your-Python-package

## 8. Ability to easily add filters to template engine

Release 0.17
============

- Email handling
  - Sync with imap/pop accounts
  - Thread responses
  - Track open/forward rates

- SMS Handling
  - Track responses

- Better API - integrate with docstring
- Debug bar setup - with docstring support
- Prospector integration
- Unit testing integration

Release 0.18
============

- NoSQL Integration with tinydb
- Websocket integration

Release 0.20
============

- Tasks and Daemon Processes
- SSO Integration

Release 0.22
============


