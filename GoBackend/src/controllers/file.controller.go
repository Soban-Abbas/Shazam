package controllers

import (
	"net/http"
	"path/filepath"
	"shazam-backend/src/services"

	"github.com/gin-gonic/gin"
)

func UploadFileController(c *gin.Context) {
	file, err := c.FormFile("audio")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No audio file received"})
		return
	}

	savePath := "./temp/" + filepath.Base(file.Filename)
	if err := c.SaveUploadedFile(file, savePath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Could not save file"})
		return
	}

	result, err := services.SendToPythonAPI(savePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Python service failed"})
		return
	}

	c.JSON(http.StatusOK, result)
}