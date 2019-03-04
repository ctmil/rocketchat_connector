# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date,timedelta
from dateutil import relativedelta
from rocketchat_API.rocketchat import RocketChat

class RocketChatServer(models.Model):
	_name = 'rocketchat.server'
	_description = 'rocketchat.server'

	name = fields.Char('Rocket.Chat Server')


class ResUsers(models.Model):
	_inherit = 'res.users'

	rocketchat_server_id = fields.Many2one('rocketchat.server',string='Server')
	rocketchat_user = fields.Char('Rocket.Chat user')
	rocketchat_pwd = fields.Char('Rocket.Chat password')
	rocketchat_channel = fields.Char('Rocket.Chat channel')


class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	@api.multi
	def action_invoice_open(self):
		context = self._context
		res = super(AccountInvoice, self).action_invoice_open()
		current_uid = context.get('uid')
		user = self.env['res.users'].browse(current_uid)
		if user.rocketchat_server_id and user.rocketchat_user and user.rocketchat_pwd and user.rocketchat_channel:
			rocket = RocketChat(user.rocketchat_user, user.rocketchat_pwd, server_url=user.rocketchat_server_id.name, proxies={})
			try:
				for rec in self:
					if rec.type != 'out_invoice':
						continue
					msg = 'Se acaba de validar la factura ' + str(rec.display_name) + ' del cliente ' + rec.partner_id.name + ' por un monto '\
							 + str(rec.amount_total) + ' ' + rec.currency_id.name
					rocket.chat_post_message(msg, channel=user.rocketchat_channel, alias=user.rocketchat_user).json()	
			except:
				pass
		return res
