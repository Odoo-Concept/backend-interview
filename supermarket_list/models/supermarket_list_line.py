# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SupermarketListLine(models.Model):
    _name = 'supermarket.list.line'
    _description = 'Supermarket list line'

    list_id = fields.Many2one('supermarket.list', string='Lista', ondelete='cascade', required=True)
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    quantity = fields.Float(string='Cantidad', default=1.0)
    purchased = fields.Boolean(string='Comprado', default=False)
    purchased_by = fields.Many2one('res.users', string='Comprado por', readonly=True)
    purchased_date = fields.Datetime(string='Fecha de compra', readonly=True)
    list_state = fields.Selection([
        ('draft', 'Borrador'),
        ('progress', 'En Progreso'),
        ('done', 'Completada')
    ], string='Estado', related="list_id.state")
    
    @api.onchange('purchased')
    def onchange_purchased(self):
        # Si se cambia el campo purchased, validar que el usuario sea el responsable de la lista
        for record in self:
            if self.env.uid != record.list_id.responsible_id.id:
                    raise ValidationError(_('Solo el usuario responsable puede modificar este campo.'))

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        return rec

    def write(self, vals):
        res = super().write(vals)

        # Si se marca como comprado, registrar usuario y fecha, y actualizar estado de la lista
        if 'purchased' in vals:
            for rec in self:
                if rec.purchased and not rec.purchased_by:
                    rec.purchased_by = self.env.user
                    rec.purchased_date = fields.Datetime.now()
                elif not rec.purchased:
                    # si se desmarca, limpiar datos de comprador
                    rec.purchased_by = False
                    rec.purchased_date = False

                # actualiza estado padre, si todos los items están comprados => done; si no => progress
                parent = rec.list_id
                if all(line.purchased for line in parent.line_ids):
                    parent.state = 'done'
                else:
                    # si esta en estado done y ahora hay ítems no comprados, pasa a progress
                    if parent.state == 'done':
                        parent.state = 'progress'
        return res

    def unlink(self):
        # Permitir eliminar líneas en borrador o en progreso; si la lista está completada impedir eliminación
        for rec in self:
            if rec.list_id.state == 'done':
                raise ValidationError(_('No se pueden eliminar ítems de una lista completada.'))
        return super().unlink()
