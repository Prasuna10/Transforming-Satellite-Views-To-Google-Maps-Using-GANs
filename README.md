# Transforming-Satellite-Views-To-Google-Maps-Using-GANs
Conversion Of Satellite Images to Google Maps Using Gans:-
Reference Paper: Vaishali Ingale, Rishabh Singh, Pragati Patwal “Image toImage Translation : Generating maps from satellite images” arXiv:2105.09253, 19 May 2021 IEEE Access https://arxiv.org/pdf/2105.09253

Dataset Link : https://www.kaggle.com/datasets/vikramtiwari/pix2pix-dataset/data?select=maps

The primary objective of this project is to convert images taken from satellites into appropriate Google map images. Althoughseveral models are available for image-to-image translation, the translations provided by them are not clear. Our goals with the Conditional Generative Adversarial Networks model is to minimize loss, enhance image quality, and have control over the output.It will be very beneficial for the future of urban planning assistance, navigation, and recognition of water bodies.

Generator Architecture Of Conditional Gan:

![generator](https://github.com/Prasuna10/Transforming-Satellite-Views-To-Google-Maps-Using-GANs/assets/96649154/d3e0f998-2703-4801-b6f2-c0f04fcd3dba) 

While the Discriminator is not in use, the Generator is getting ready. The predictions made by the Generator can be used to train the generator and improve from the previous state after the Generator's bogus data has been used to train the discriminator in an effort to trick it. The above figure shows the generator model is built using u-net architecture.

Descrimintator Architecture Of Conditional Gan: 

![descriminator](https://github.com/Prasuna10/Transforming-Satellite-Views-To-Google-Maps-Using-GANs/assets/96649154/197ce7e9-8819-4c6c-b183-31105358730f)

 In the fig Discriminator is trained while the Generator is not
 running. The organization is only spreading forward at this
 point; back-proliferation is not yet complete. The Discriminator
 is trained on actual data for n epochs to test if it can
 successfully forecast them. Moreover, during this step, the
 Discriminator is trained on the Generator's false generated data
 to test its accuracy in recognising them as fake.

Comparison between CNN AND CGAN Results:

CNN RESULTS:

![cnn predicted](https://github.com/Prasuna10/Transforming-Satellite-Views-To-Google-Maps-Using-GANs/assets/96649154/d19b35ae-9c3c-40b6-88d4-9a76eb8cf139)

CGAN RESULTS:

![cgan predicted](https://github.com/Prasuna10/Transforming-Satellite-Views-To-Google-Maps-Using-GANs/assets/96649154/568beda7-03fa-46bb-8de1-14fc0c04b6fa)

The effectiveness of a U-Net based conditional GAN was
 successfully implemented and trained on a set of 1000 images,
 each divided into corresponding satellite imagery and map
 data, resized to 256x256 pixels. The model, structured with
 downsampling and upsampling layers along with Batch
 Normalization and LeakyReLU activations, was compiled with
 Adam optimizer and binary cross entropy loss. Upon training
 over 50 epochs, CGAN performed well than CNN.
 
FRONTEND CONVERSION:

![fronend](https://github.com/Prasuna10/Transforming-Satellite-Views-To-Google-Maps-Using-GANs/assets/96649154/8e89399d-12d4-43b0-9f9d-2181b8e73ca7)




