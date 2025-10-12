#-*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import AccessError


class SupermarketList(models.Model):
    _name = 'supermarket.list'
    _description = 'Supermarket list'
    _rec_name = 'name'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Char(string='Descripción',)
    responsible_id = fields.Many2one('res.users',
                                     string='Responsable',
                                     required=True,
                                     default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('progress', 'En Progreso'),
        ('done', 'Completada')
    ], string='Estado', default='draft', copy=False)
    line_ids = fields.One2many('supermarket.list.line',
                               'list_id',
                               string='Ítems', copy=True)

    note = fields.Text(string='Notas')


    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_set_progress(self):
        for rec in self:
            # no permitir pasar a progreso si no tiene ítems
            if not rec.line_ids:
                raise exceptions.UserError(_('La lista debe tener al menos un ítem para comenzar.'))
            rec.state = 'progress'

    def action_set_done(self):
        for rec in self:
            # validar que todos los items estén comprados
            not_bought = rec.line_ids.filtered(lambda l: not l.purchased)
            if not_bought:
                raise exceptions.UserError(_('No se puede marcar como completada: algunos ítems no están comprados.'))
            rec.state = 'done'


