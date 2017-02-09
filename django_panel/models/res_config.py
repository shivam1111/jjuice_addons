# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class django_panel_settings(osv.osv_memory):
    _name = 'django.panel.settings'
    _inherit = 'res.config.settings'
    
    def set_default_aws_access_id(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'aws_access_id', (myself.aws_access_id or '').strip(), groups=['base.group_system'], context=None)

    def get_default_aws_access_id(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        aws_access_id = params.get_param(cr, uid, 'aws_access_id',default='',context=context)        
        return dict(aws_access_id=aws_access_id)                                            
        
    def set_default_aws_secret_key(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'aws_secret_key', (myself.aws_secret_key or '').strip(), groups=['base.group_system'], context=None)

    def get_default_aws_secret_key(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        aws_secret_key = params.get_param(cr, uid, 'aws_secret_key',default='',context=context)        
        return dict(aws_secret_key=aws_secret_key) 
    
    def set_default_website_banner_key(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'website_banner_key', (myself.website_banner_key or '').strip(), groups=['base.group_system'], context=None)

    def get_default_website_banner_key(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        website_banner_key = params.get_param(cr, uid, 'website_banner_key',default='',context=context)        
        return dict(website_banner_key=website_banner_key)                                                                                                   

    def set_default_root_bucket(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'root_bucket', (myself.root_bucket or '').strip(), groups=['base.group_system'], context=None)
 
    def get_default_root_bucket(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        root_bucket = params.get_param(cr, uid, 'root_bucket',default='',context=context)        
        return dict(root_bucket=root_bucket)                                                                                                   

    def set_default_aws_base_url(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'aws_base_url', (myself.aws_base_url or '').strip(), groups=['base.group_system'], context=None)
 
    def get_default_aws_base_url(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        aws_base_url = params.get_param(cr, uid, 'aws_base_url',default='',context=context)        
        return dict(aws_base_url=aws_base_url)                                                                                                   

    def set_default_website_policy_key(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'website_policy_key', (myself.website_policy_key or '').strip(), groups=['base.group_system'], context=None)

    def get_default_website_policy_key(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        website_policy_key = params.get_param(cr, uid, 'website_policy_key',default='',context=context)        
        return dict(website_policy_key=website_policy_key)

    def set_default_meta_keywords(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'meta_keywords', (myself.meta_keywords or '').strip(), groups=['base.group_system'], context=None)

    def get_default_meta_keywords(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        meta_keywords = params.get_param(cr, uid, 'meta_keywords',default='',context=context)        
        return dict(meta_keywords=meta_keywords)                                                                                                       

    def set_default_meta_description(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'meta_description', (myself.meta_description or '').strip(), groups=['base.group_system'], context=None)

    def get_default_meta_description(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        meta_description = params.get_param(cr, uid, 'meta_description',default='',context=context)        
        return dict(meta_description=meta_description)

    def set_default_site_name(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        myself = self.browse(cr,uid,ids[0],context=context)
        params.set_param(cr, uid, 'site_name', (myself.site_name or '').strip(), groups=['base.group_system'], context=None)

    def get_default_site_name(self,cr,uid,ids,context=None):
        params = self.pool.get('ir.config_parameter')
        site_name = params.get_param(cr, uid, 'site_name',default='',context=context)        
        return dict(site_name=site_name)                                                                                                                
                                                                                                              
                                                                                          
    
    _columns = {
            'site_name':fields.char("Site Name"),
            'aws_access_id' : fields.char("AWS Access ID"),
            'aws_secret_key' : fields.char('AWS Secret Key'),
            'root_bucket':fields.char("Root Bucket"),
            'website_banner_key' : fields.char("Website Banner Bucket"),
            'website_policy_key' : fields.char("Website Policy Bucket"),
            'aws_base_url':fields.char("S3 Base URL",help="This is required so that when determining the url we do not have to send extra request to determine the location of the bucket"),
            'meta_keywords':fields.text("Meta Keywords"),
            'meta_description':fields.text('Meta Description')
        }