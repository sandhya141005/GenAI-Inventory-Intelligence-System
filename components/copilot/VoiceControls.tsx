"use client";

import { useEffect, useRef, useState } from "react";
import { Mic, MicOff, Volume2, VolumeX } from "lucide-react";
import { Button } from "@/components/ui/button";

export const SUPPORTED_LANGUAGES = [
  { code: "en-IN", label: "English" },
  { code: "ta-IN", label: "Tamil" },
  { code: "hi-IN", label: "Hindi" },
  { code: "te-IN", label: "Telugu" },
  { code: "kn-IN", label: "Kannada" },
  { code: "ml-IN", label: "Malayalam" },
  { code: "mr-IN", label: "Marathi" },
  { code: "bn-IN", label: "Bengali" },
];

interface VoiceControlsProps {
  lang: string;
  onLangChange: (lang: string) => void;
  onTranscript: (text: string) => void;
  speakEnabled: boolean;
  onSpeakEnabledChange: (enabled: boolean) => void;
}

export function VoiceControls({ lang, onLangChange, onTranscript, speakEnabled, onSpeakEnabledChange }: VoiceControlsProps) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = lang;

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
    };
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognitionRef.current = recognition;
    return () => recognition.stop();
  }, [lang, onTranscript]);

  function toggleListening() {
    if (!recognitionRef.current) {
      alert("Speech recognition isn't supported in this browser. Try Chrome or Edge.");
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <select
        value={lang}
        onChange={(e) => onLangChange(e.target.value)}
        className="h-10 rounded-lg border border-border bg-background px-2 text-xs outline-none"
      >
        {SUPPORTED_LANGUAGES.map((l) => (
          <option key={l.code} value={l.code}>{l.label}</option>
        ))}
      </select>

      <Button
        type="button"
        variant={isListening ? "primary" : "ghost"}
        size="icon"
        onClick={toggleListening}
        title={isListening ? "Stop listening" : "Speak your question"}
        className="h-10 w-10 rounded-lg"
      >
        {isListening ? <MicOff className="h-4 w-4 animate-pulse" /> : <Mic className="h-4 w-4" />}
      </Button>

      <Button
        type="button"
        variant={speakEnabled ? "primary" : "ghost"}
        size="icon"
        onClick={() => onSpeakEnabledChange(!speakEnabled)}
        title={speakEnabled ? "Voice replies on" : "Voice replies off"}
        className="h-10 w-10 rounded-lg"
      >
        {speakEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
      </Button>
    </div>
  );
}

export function speak(text: string, lang: string) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;

  const voices = window.speechSynthesis.getVoices();
  const match = voices.find((v) => v.lang === lang) || voices.find((v) => v.lang.startsWith(lang.split("-")[0]));
  if (match) {
    utterance.voice = match;
  } else {
    console.warn(`No voice found for ${lang} — falling back to default.`);
  }

  window.speechSynthesis.speak(utterance);
}