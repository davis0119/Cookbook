HW		 := hw2
ZIPFILES := k8s

.PHONY: zip
zip:
	zip -r $(HW)_submission.zip $(ZIPFILES)
