## Script (Python) "content_edit"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=''
##


returning = context.content_edit_impl(state, id)
context.REQUEST.RESPONSE.expireCookie('statusmessages', path='/')
return returning
