from __future__ import print_function

import urllib
import os
import subprocess
import boto3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(SCRIPT_DIR, 'lib')

def downloadFromS3(strBucket, strKey, strFile):
  s3_client = boto3.client('s3')
  s3_client.download_file(strBucket, strKey, strFile)

def uploadToS3(strFile, strBucket, strKey):
  s3_client = boto3.client('s3')
  s3_client.upload_file(strFile, strBucket, strKey, ExtraArgs={'ACL':'public-read'})

def handler(event, context):
  try:
    # Download yolo weights
    strBucket = 'darknet-images-latinoware'
    strKey = 'darknet/yolov3.weights'
    strWeightFile = '/tmp/yolov3.weights'
    downloadFromS3(strBucket, strKey, strWeightFile)

    for imagePath in map(lambda r: r['s3']['object']['key'], event['Records']):
      # Download image from bucket
      imageFile = imagePath.split('/').pop()
      imageFilePath = '/tmp/{}'.format(imageFile)
      downloadFromS3(strBucket, imagePath, imageFilePath)
      
      predictionsPath = '/tmp/predictions.png'
      command = './darknet detect cfg/yolov3.cfg {} {} -out /tmp/predictions'.format(
          strWeightFile,
          imageFilePath
      )
      print(command)

      try:
        print('Start')
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        print('Finish')
        # upload predictions to bucket
        print(output)
        predictionsFile = '{}.png'.format(os.path.splitext(imageFile)[0])
        predictionsKey = 'predictions/{}'.format(predictionsFile)
        uploadToS3(predictionsPath, strBucket, predictionsKey)
      except subprocess.CalledProcessError as e:
        print('Error')
        print(e.output)
  except Exception as e:
    print('Error')
    print(e)
    raise e
  return 0 
