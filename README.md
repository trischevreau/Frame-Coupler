# Frame-Coupler

This little program selects common images from a set of videos, using the display of a digital clock in the field of view.

These videos should be MPEG-4 files, which will be converted to gray JPEG frames.

The digital clock is supposed to be of this model : https://www.youtube.com/watch?v=rf2Lmfqi5ZM

It uses Tesseract for the OCR https://github.com/tesseract-ocr

You can use 'verify_librairies.py' to see which imports are missing.

The file 'run_parameters.py' contains variables that you should change to match your needs and your installation of pytesseract.

# Work Flow

```mermaid
graph LR
	s1((Step 1 : conversion))
	s2((Step 2 : raw OCR))
	s3((Step 3 : clock fitting))
	s4((Step 4 : frame coupling))
	
	v(video 1)
	rawocr(raw ocr results)
	ect(estimated clock times for video 1)
	ect2(estimated clock times for video 2)
	fr(frames & associated timestamps)
	cf(coupled frames)
	v2(video 2)
	_(...)
	
	v --> s1
	s1 --> fr
	fr -->|sampling| s2
	s2 --> rawocr
	fr -->|only timestamps| s3
	rawocr --> s3
	s3 --> ect
	ect --> s4
	v2 --> _ --> ect2
	ect2 --> s4
	s4 --> cf
```

