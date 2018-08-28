using System;
using System.IO;
using System.Collections.Generic;
using Failbetter.Core;
using Skyless.Assets.Code.Skyless.Utilities.Serialization;
using Newtonsoft.Json;
using ICSharpCode.SharpZipLib.Tar;
using ICSharpCode.SharpZipLib.GZip;

namespace Sunless_Skies_Serialization
{
    class Reserialize
    {
        static string latest = "2018-07-31";
        static string basepath = "[SET PATH HERE]\\{0}\\{1}\\";
        static string srcpath = String.Format(basepath, latest, "TextAsset");
        static string dstpath = String.Format(basepath, latest, "Decoded");
        static Logger logger = new Logger();
        static BinarySerializationService bss = new BinarySerializationService(null, null);
        static IList<Domicile> dl;
        static IList<Quality> ql;
        static IList<Exchange> exl;
        static IList<Setting> sl;
        static IList<Area> al;
        static IList<Prospect> pl;
        static IList<Bargain> bl;
        static IList<Persona> prl;
        static IList<Event> el;

        private static readonly JsonSerializerSettings _settings = new JsonSerializerSettings()
        {
            DefaultValueHandling = DefaultValueHandling.Ignore,
            NullValueHandling = NullValueHandling.Ignore,
            ReferenceLoopHandling = ReferenceLoopHandling.Ignore
        };

        public static void SerializeToStream<T>(string path, T data)
        {
            using (FileStream fs = new FileStream(path, FileMode.Create))
            {
                using (StreamWriter sw = new StreamWriter(fs))
                {
                    using (JsonTextWriter jtw = new JsonTextWriter(sw))
                    {
                        Newtonsoft.Json.JsonSerializer.Create(_settings).Serialize(jtw, (object) data);
                    }
                }
            }
        }

        /* areas bargains domiciles events exchanges personae prospects qualities settings */
        static void LoadData()
        {
            dl = bss.DeserializeDomicilesFromResources(new BinaryReader(File.Open(srcpath + "domiciles.txt", FileMode.Open)));
            ql = bss.DeserializeQualitiesFromResources(new BinaryReader(File.Open(srcpath + "qualities.txt", FileMode.Open)));
            exl = bss.DeserializeExchangesFromResources(new BinaryReader(File.Open(srcpath + "exchanges.txt", FileMode.Open)));
            sl = bss.DeserializeSettingsFromResources(new BinaryReader(File.Open(srcpath + "settings.txt", FileMode.Open)));
            al = bss.DeserializeAreasFromResources(new BinaryReader(File.Open(srcpath + "areas.txt", FileMode.Open)));
            pl = bss.DeserializeProspectsFromResources(new BinaryReader(File.Open(srcpath + "prospects.txt", FileMode.Open)));
            bl = bss.DeserializeBargainsFromResources(new BinaryReader(File.Open(srcpath + "bargains.txt", FileMode.Open)));
            prl = bss.DeserializePersonaeFromResources(new BinaryReader(File.Open(srcpath + "personas.txt", FileMode.Open)));
            el = bss.DeserializeEventsFromResources(new BinaryReader(File.Open(srcpath + "events.txt", FileMode.Open)));
        }

        static void Dump()
        {
            SerializeToStream(dstpath + "domiciles.txt", dl);
            SerializeToStream(dstpath + "qualities.txt", ql);
            SerializeToStream(dstpath + "exchanges.txt", exl);
            SerializeToStream(dstpath + "settings.txt", sl);
            SerializeToStream(dstpath + "areas.txt", al);
            SerializeToStream(dstpath + "prospects.txt", pl);
            SerializeToStream(dstpath + "bargains.txt", bl);
            SerializeToStream(dstpath + "personae.txt", prl);
            SerializeToStream(dstpath + "events.txt", el);
        }

        static void Zip()
        {
            Stream outstream = File.Create(dstpath + "data.tar.gz");
            Stream gzipstream = new GZipOutputStream(outstream);
            TarArchive tar = TarArchive.CreateOutputTarArchive(gzipstream);

            AddDirectoryFilesToTar(tar, dstpath, true);

            tar.Close();
        }

        static void AddDirectoryFilesToTar(TarArchive tarArchive, string sourceDirectory, bool recurse)
        {
            TarEntry tarEntry = TarEntry.CreateEntryFromFile(sourceDirectory);
            tarArchive.WriteEntry(tarEntry, false);

            string[] filenames = Directory.GetFiles(sourceDirectory);
            foreach (string filename in filenames)
            {
                tarEntry = TarEntry.CreateEntryFromFile(filename);
                tarArchive.WriteEntry(tarEntry, true);
            }

            if (recurse)
            {
                string[] directories = Directory.GetDirectories(sourceDirectory);
                foreach (string directory in directories)
                    AddDirectoryFilesToTar(tarArchive, directory, recurse);
            }
        }

        static void Main(string[] args)
        {
            Console.WriteLine("loading...");
            LoadData();
            Console.WriteLine("writing...");
            Dump();
            Console.WriteLine("zipping...");
            Zip();
            Console.WriteLine("done.");
            Console.ReadKey();
        }
    }
}