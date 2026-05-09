'use client'

import { useRef, useState, useCallback } from 'react'

export interface AudioRecorderState {
  isRecording: boolean
  audioBlob: Blob | null
  analyserNode: AnalyserNode | null
  duration: number
  start: () => Promise<void>
  stop: () => void
  reset: () => void
}

export function useAudioRecorder(): AudioRecorderState {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [analyserNode, setAnalyserNode] = useState<AnalyserNode | null>(null)
  const [duration, setDuration] = useState(0)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const audioCtxRef = useRef<AudioContext | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const startTimeRef = useRef<number>(0)

  const start = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    streamRef.current = stream

    const audioCtx = new AudioContext()
    audioCtxRef.current = audioCtx
    const source = audioCtx.createMediaStreamSource(stream)
    const analyser = audioCtx.createAnalyser()
    analyser.fftSize = 256
    source.connect(analyser)
    setAnalyserNode(analyser)

    const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    mediaRecorderRef.current = recorder
    chunksRef.current = []

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data)
    }

    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
      setAudioBlob(blob)
    }

    recorder.start()
    startTimeRef.current = Date.now()
    setIsRecording(true)
    setDuration(0)

    timerRef.current = setInterval(() => {
      setDuration(Math.floor((Date.now() - startTimeRef.current) / 1000))
    }, 1000)
  }, [])

  const stop = useCallback(() => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop()
    }
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    streamRef.current?.getTracks().forEach((t) => t.stop())
    audioCtxRef.current?.close()
    setIsRecording(false)
    setAnalyserNode(null)
  }, [])

  const reset = useCallback(() => {
    setAudioBlob(null)
    setDuration(0)
    chunksRef.current = []
  }, [])

  return { isRecording, audioBlob, analyserNode, duration, start, stop, reset }
}
