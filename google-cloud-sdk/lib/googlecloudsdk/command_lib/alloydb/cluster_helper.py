# -*- coding: utf-8 -*- #
# Copyright 2022 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helper functions for constructing and validating AlloyDB cluster requests."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.alloydb import flags
from googlecloudsdk.core import properties


def _ConstructAutomatedBackupPolicy(alloydb_messages, args):
  """Returns the automated backup policy based on args."""
  backup_policy = alloydb_messages.AutomatedBackupPolicy()
  if args.disable_automated_backup:
    backup_policy.enabled = False
  elif args.automated_backup_days_of_week:
    backup_policy.enabled = True
    backup_policy.weeklySchedule = alloydb_messages.WeeklySchedule(
        daysOfWeek=args.automated_backup_days_of_week,
        startTimes=args.automated_backup_start_times,
    )
    if args.automated_backup_retention_count:
      backup_policy.quantityBasedRetention = (
          alloydb_messages.QuantityBasedRetention(
              count=args.automated_backup_retention_count))
    elif args.automated_backup_retention_period:
      backup_policy.timeBasedRetention = (
          alloydb_messages.TimeBasedRetention(retentionPeriod='{}s'.format(
              args.automated_backup_retention_period)))
    if args.automated_backup_window:
      backup_policy.backupWindow = '{}s'.format(args.automated_backup_window)
    kms_key = flags.GetAndValidateKmsKeyName(
        args, flag_overrides=flags.GetAutomatedBackupKmsFlagOverrides())
    if kms_key:
      encryption_config = alloydb_messages.EncryptionConfig()
      encryption_config.kmsKeyName = kms_key
      backup_policy.encryptionConfig = encryption_config
    backup_policy.location = args.region
  return backup_policy


def _ConstructPitrConfig(alloydb_messages, args):
  """Returns the pitr config based on args."""
  pitr_config = alloydb_messages.PitrConfig()
  if args.disable_pitr:
    pitr_config.enabled = False
  elif args.pitr_log_retention_window:
    pitr_config.enabled = True
    pitr_config.logRetentionWindow = '{}s'.format(
        args.pitr_log_retention_window)
  return pitr_config


def _ConstructClusterForCreateRequestGA(alloydb_messages, args):
  """Returns the cluster for GA create request based on args."""
  cluster = alloydb_messages.Cluster()
  cluster.network = args.network
  cluster.initialUser = alloydb_messages.UserPassword(
      password=args.password, user='postgres')
  kms_key = flags.GetAndValidateKmsKeyName(args)
  if kms_key:
    encryption_config = alloydb_messages.EncryptionConfig()
    encryption_config.kmsKeyName = kms_key
    cluster.encryptionConfig = encryption_config

  if args.disable_automated_backup or args.automated_backup_days_of_week:
    cluster.automatedBackupPolicy = _ConstructAutomatedBackupPolicy(
        alloydb_messages, args)

  return cluster


def _ConstructClusterForCreateRequestAlphaBeta(alloydb_messages, args):
  """Returns the cluster for alpha or beta create request based on args."""
  cluster = _ConstructClusterForCreateRequestGA(alloydb_messages, args)

  if args.disable_pitr or args.pitr_log_retention_window:
    cluster.pitrConfig = _ConstructPitrConfig(alloydb_messages, args)

  return cluster


def ConstructCreateRequestFromArgsGA(alloydb_messages, location_ref, args):
  """Returns the cluster create request for GA track based on args."""
  cluster = _ConstructClusterForCreateRequestGA(alloydb_messages, args)

  return alloydb_messages.AlloydbProjectsLocationsClustersCreateRequest(
      cluster=cluster,
      clusterId=args.cluster,
      parent=location_ref.RelativeName())


def ConstructCreateRequestFromArgsAlphaBeta(alloydb_messages, location_ref,
                                            args):
  """Returns the cluster create request for alpha and beta tracks based on args.
  """
  cluster = _ConstructClusterForCreateRequestAlphaBeta(alloydb_messages, args)

  return alloydb_messages.AlloydbProjectsLocationsClustersCreateRequest(
      cluster=cluster,
      clusterId=args.cluster,
      parent=location_ref.RelativeName())


def _ConstructBackupSourceForRestoreRequest(alloydb_messages, resource_parser,
                                            args):
  """Returns the backup source for restore request."""
  backup_ref = resource_parser.Create(
      'alloydb.projects.locations.backups',
      projectsId=properties.VALUES.core.project.GetOrFail,
      locationsId=args.region,
      backupsId=args.backup)
  backup_source = alloydb_messages.BackupSource(
      backupName=backup_ref.RelativeName())
  return backup_source


def _ConstructClusterResourceForRestoreRequest(alloydb_messages, args):
  """Returns the cluster resource for restore request."""
  cluster_resource = alloydb_messages.Cluster()
  cluster_resource.network = args.network
  kms_key = flags.GetAndValidateKmsKeyName(args)
  if kms_key:
    encryption_config = alloydb_messages.EncryptionConfig()
    encryption_config.kmsKeyName = kms_key
    cluster_resource.encryptionConfig = encryption_config
  return cluster_resource


def ConstructRestoreRequestFromArgsGA(alloydb_messages, location_ref,
                                      resource_parser, args):
  """Returns the cluster restore request for GA track based on args."""
  cluster_resource = _ConstructClusterResourceForRestoreRequest(
      alloydb_messages, args)

  backup_source = _ConstructBackupSourceForRestoreRequest(
      alloydb_messages, resource_parser, args)

  return alloydb_messages.AlloydbProjectsLocationsClustersRestoreRequest(
      parent=location_ref.RelativeName(),
      restoreClusterRequest=alloydb_messages.RestoreClusterRequest(
          backupSource=backup_source,
          clusterId=args.cluster,
          cluster=cluster_resource,
      ))


def ConstructRestoreRequestFromArgsAlphaBeta(alloydb_messages, location_ref,
                                             resource_parser, args):
  """Returns the cluster restore request for alpha and beta tracks based on args.
  """
  cluster_resource = _ConstructClusterResourceForRestoreRequest(
      alloydb_messages, args)

  backup_source, pitr_source = None, None
  if args.backup:
    backup_source = _ConstructBackupSourceForRestoreRequest(
        alloydb_messages, resource_parser, args)
  else:
    cluster_ref = resource_parser.Create(
        'alloydb.projects.locations.clusters',
        projectsId=properties.VALUES.core.project.GetOrFail,
        locationsId=args.region,
        clustersId=args.source_cluster)
    pitr_source = alloydb_messages.PitrSource(
        cluster=cluster_ref.RelativeName(),
        pointInTime=args.point_in_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

  return alloydb_messages.AlloydbProjectsLocationsClustersRestoreRequest(
      parent=location_ref.RelativeName(),
      restoreClusterRequest=alloydb_messages.RestoreClusterRequest(
          backupSource=backup_source,
          pitrSource=pitr_source,
          clusterId=args.cluster,
          cluster=cluster_resource,
      ))


def _ConstructClusterAndMaskForPatchRequestGA(alloydb_messages, args):
  cluster = alloydb_messages.Cluster()
  update_masks = []

  if (args.disable_automated_backup or args.automated_backup_days_of_week or
      args.clear_automated_backup):
    cluster.automatedBackupPolicy = _ConstructAutomatedBackupPolicy(
        alloydb_messages, args)
    update_masks.append('automated_backup_policy')
  return cluster, update_masks


def _ConstructClusterAndMaskForPatchRequestAlphaBeta(alloydb_messages, args):
  cluster, update_masks = _ConstructClusterAndMaskForPatchRequestGA(
      alloydb_messages, args)
  if args.disable_pitr or args.pitr_log_retention_window:
    cluster.pitrConfig = _ConstructPitrConfig(alloydb_messages, args)
    update_masks.append('pitr_config')
  return cluster, update_masks


def ConstructPatchRequestFromArgsGA(alloydb_messages, cluster_ref, args):
  """Returns the cluster patch request for GA release track based on args."""
  cluster, update_masks = _ConstructClusterAndMaskForPatchRequestGA(
      alloydb_messages, args)
  return alloydb_messages.AlloydbProjectsLocationsClustersPatchRequest(
      name=cluster_ref.RelativeName(),
      cluster=cluster,
      updateMask=','.join(update_masks))


def ConstructPatchRequestFromArgsAlphaBeta(alloydb_messages, cluster_ref, args):
  """Returns the cluster patch request for alpha and beta release tracks based on args.
  """
  cluster, update_masks = _ConstructClusterAndMaskForPatchRequestAlphaBeta(
      alloydb_messages, args)
  return alloydb_messages.AlloydbProjectsLocationsClustersPatchRequest(
      name=cluster_ref.RelativeName(),
      cluster=cluster,
      updateMask=','.join(update_masks))
