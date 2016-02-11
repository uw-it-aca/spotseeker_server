# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SharedSpaceReference'
        db.create_table('spotseeker_server_sharedspacereference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('share_space', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['spotseeker_server.ShareSpace'])),
            ('date_submitted', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('spotseeker_server', ['SharedSpaceReference'])

        # Adding model 'ShareSpaceRecipient'
        db.create_table('spotseeker_server_sharespacerecipient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.CharField')(default=None, max_length=16, null=True, blank=True)),
            ('recipient', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('spotseeker_server', ['ShareSpaceRecipient'])

        # Adding model 'ShareSpace'
        db.create_table('spotseeker_server_sharespace', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('space', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['spotseeker_server.Spot'])),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['spotseeker_server.ShareSpaceSender'])),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['spotseeker_server.ShareSpaceRecipient'])),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('date_shared', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('spotseeker_server', ['ShareSpace'])

        # Adding model 'ShareSpaceSender'
        db.create_table('spotseeker_server_sharespacesender', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('sender', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('spotseeker_server', ['ShareSpaceSender'])


    def backwards(self, orm):
        # Deleting model 'SharedSpaceReference'
        db.delete_table('spotseeker_server_sharedspacereference')

        # Deleting model 'ShareSpaceRecipient'
        db.delete_table('spotseeker_server_sharespacerecipient')

        # Deleting model 'ShareSpace'
        db.delete_table('spotseeker_server_sharespace')

        # Deleting model 'ShareSpaceSender'
        db.delete_table('spotseeker_server_sharespacesender')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'oauth_provider.consumer': {
            'Meta': {'object_name': 'Consumer'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'xauth_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'spotseeker_server.favoritespot': {
            'Meta': {'object_name': 'FavoriteSpot'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'spot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spotseeker_server.Spot']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'spotseeker_server.sharedspacereference': {
            'Meta': {'object_name': 'SharedSpaceReference'},
            'date_submitted': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'share_space': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spotseeker_server.ShareSpace']"})
        },
        'spotseeker_server.sharespace': {
            'Meta': {'object_name': 'ShareSpace'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'date_shared': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spotseeker_server.ShareSpaceRecipient']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spotseeker_server.ShareSpaceSender']"}),
            'space': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spotseeker_server.Spot']"})
        },
        'spotseeker_server.sharespacerecipient': {
            'Meta': {'object_name': 'ShareSpaceRecipient'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '16', 'null': 'True', 'blank': 'True'})
        },
        'spotseeker_server.sharespacesender': {
            'Meta': {'object_name': 'ShareSpaceSender'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'spotseeker_server.spacereview': {
            'Meta': {'object_name': 'SpaceReview'},
            'date_published': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_submitted': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'original_review': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            'published_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'published_by'", 'null': 'True', 'to': "orm['auth.User']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {}),
            'review': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            'reviewer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reviewer'", 'to': "orm['auth.User']"}),
            'space': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spotseeker_server.Spot']"})
        },
        'spotseeker_server.spot': {
            'Meta': {'object_name': 'Spot'},
            'building_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'capacity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'display_access_restrictions': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'etag': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'external_id': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'floor': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'height_from_sea_level': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '8', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '8'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '8'}),
            'manager': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'room_number': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'spottypes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'spots'", 'to': "orm['spotseeker_server.SpotType']", 'max_length': '50', 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        'spotseeker_server.spotavailablehours': {
            'Meta': {'object_name': 'SpotAvailableHours'},
            'day': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'spot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spotseeker_server.Spot']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
        },
        'spotseeker_server.spotextendedinfo': {
            'Meta': {'unique_together': "(('spot', 'key'),)", 'object_name': 'SpotExtendedInfo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'spot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spotseeker_server.Spot']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'spotseeker_server.spotimage': {
            'Meta': {'object_name': 'SpotImage'},
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'display_index': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'etag': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'spot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spotseeker_server.Spot']"}),
            'upload_application': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upload_user': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'spotseeker_server.spottype': {
            'Meta': {'object_name': 'SpotType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'spotseeker_server.trustedoauthclient': {
            'Meta': {'object_name': 'TrustedOAuthClient'},
            'bypasses_user_authorization': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'consumer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oauth_provider.Consumer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_trusted': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['spotseeker_server']