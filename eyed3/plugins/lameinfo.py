import os
import math
from eyed3.utils import formatSize
from eyed3.utils.console import printMsg, boldText, Fore, HEADER_COLOR
from eyed3.plugins import LoaderPlugin


class LameInfoPlugin(LoaderPlugin):
    NAMES = ["lameinfo", "xing"]
    SUMMARY = u"Outputs lame header (if one exists) for file."
    DESCRIPTION = (
        u"The 'lame' (or xing) header provides extra information about the mp3 "
         "that is useful to players and encoders but not officially part of "
         "the mp3 specification. Variable bit rate mp3s, for example, use this "
         "header.\n\n"
         "For more details see "
         "`here <http://gabriel.mp3-tech.org/mp3infotag.html>`_"
         )

    def printHeader(self, filePath):
        from stat import ST_SIZE
        fileSize = os.stat(filePath)[ST_SIZE]
        size_str = formatSize(fileSize)
        print("\n%s\t%s[ %s ]%s" % (boldText(os.path.basename(filePath),
                                             HEADER_COLOR()),
                                    HEADER_COLOR(), size_str,
                                    Fore.RESET))
        print("-" * 79)

    def handleFile(self, f):
        super(LameInfoPlugin, self).handleFile(f)

        self.printHeader(f)
        if (self.audio_file is None or self.audio_file.info is None or
                not self.audio_file.info.lame_tag):
            printMsg('No LAME Tag')
            return

        format = '%-20s: %s'
        lt = self.audio_file.info.lame_tag
        if "infotag_crc" not in lt:
            try:
                printMsg('%s: %s' % ('Encoder Version', lt['encoder_version']))
            except KeyError:
                pass
            return

        values = []

        values.append(('Encoder Version', lt['encoder_version']))
        values.append(('LAME Tag Revision', lt['tag_revision']))
        values.append(('VBR Method', lt['vbr_method']))
        values.append(('Lowpass Filter', lt['lowpass_filter']))

        if "replaygain" in lt:
            try:
                peak = lt['replaygain']['peak_amplitude']
                db = 20 * math.log10(peak)
                val = '%.8f (%+.1f dB)' % (peak, db)
                values.append(('Peak Amplitude', val))
            except KeyError:
                pass
            for type in ['radio', 'audiofile']:
                try:
                    gain = lt['replaygain'][type]
                    name = '%s Replay Gain' % gain['name'].capitalize()
                    val = '%s dB (%s)' % (gain['adjustment'],
                                          gain['originator'])
                    values.append((name, val))
                except KeyError:
                    pass

        values.append(('Encoding Flags', ' '.join((lt['encoding_flags']))))
        if lt['nogap']:
            values.append(('No Gap', ' and '.join(lt['nogap'])))
        values.append(('ATH Type', lt['ath_type']))
        values.append(('Bitrate (%s)' % lt['bitrate'][1], lt['bitrate'][0]))
        values.append(('Encoder Delay', '%s samples' % lt['encoder_delay']))
        values.append(('Encoder Padding', '%s samples' % lt['encoder_padding']))
        values.append(('Noise Shaping', lt['noise_shaping']))
        values.append(('Stereo Mode', lt['stereo_mode']))
        values.append(('Unwise Settings', lt['unwise_settings']))
        values.append(('Sample Frequency', lt['sample_freq']))
        values.append(('MP3 Gain', '%s (%+.1f dB)' % (lt['mp3_gain'],
                                                      lt['mp3_gain'] * 1.5)))
        values.append(('Preset', lt['preset']))
        values.append(('Surround Info', lt['surround_info']))
        values.append(('Music Length', '%s' % formatSize(lt['music_length'])))
        values.append(('Music CRC-16', '%04X' % lt['music_crc']))
        values.append(('LAME Tag CRC-16', '%04X' % lt['infotag_crc']))

        for v in values:
            printMsg(format % (v))
