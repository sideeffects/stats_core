# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import dbs
import south.db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db = dbs['stats']
        db.dry_run = south.db.db.dry_run
        
	# Adding model 'Machine'
        db.create_table(u'stats_main_machine', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hardware_id', self.gf('django.db.models.fields.CharField')(default='', max_length=80)),
        ))
        db.send_create_signal(u'stats_main', ['Machine'])

        # Adding model 'MachineConfig'
        db.create_table(u'stats_main_machineconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('machine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats_main.Machine'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('config_hash', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('ip_address', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('graphics_card', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('graphics_card_version', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('operating_system', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('system_memory', self.gf('django.db.models.fields.FloatField')(default=0, blank=True)),
            ('system_resolution', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('number_of_processors', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('cpu_info', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('raw_user_info', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal(u'stats_main', ['MachineConfig'])

        # Adding model 'LogId'
        db.create_table(u'stats_main_logid', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('log_id', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('machine_config', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats_main.MachineConfig'])),
            ('logging_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'stats_main', ['LogId'])

        # Adding model 'Event'
        db.create_table(u'stats_main_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('show', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'stats_main', ['Event'])


    def backwards(self, orm):
	db = dbs['stats']
        db.dry_run = south.db.db.dry_run

        # Deleting model 'Machine'
        db.delete_table(u'stats_main_machine')

        # Deleting model 'MachineConfig'
        db.delete_table(u'stats_main_machineconfig')

        # Deleting model 'LogId'
        db.delete_table(u'stats_main_logid')

        # Deleting model 'Event'
        db.delete_table(u'stats_main_event')


    models = {
        u'stats_main.event': {
            'Meta': {'ordering': "('date',)", 'object_name': 'Event'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'stats_main.logid': {
            'Meta': {'ordering': "('logging_date',)", 'object_name': 'LogId'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log_id': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'logging_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'machine_config': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stats_main.MachineConfig']"})
        },
        u'stats_main.machine': {
            'Meta': {'object_name': 'Machine'},
            'hardware_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '80'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'stats_main.machineconfig': {
            'Meta': {'ordering': "('creation_date',)", 'object_name': 'MachineConfig'},
            'config_hash': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'cpu_info': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'graphics_card': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'graphics_card_version': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'machine': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['stats_main.Machine']"}),
            'number_of_processors': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'operating_system': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'raw_user_info': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'system_memory': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'system_resolution': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        }
    }

    complete_apps = ['stats_main']
