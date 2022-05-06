package dz.tools;

import com.google.gson.*;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

public class JsonFieldNameConvert {
    public static void main(String[] args) throws IOException {

        ArgumentParser parser = ArgumentParsers.newFor("Json Field Name Convert").build()
                .defaultHelp(true)
                .description("Convert Json field name conventions.");
        parser.addArgument("-i", "--input")
                .help("Input directory");
        parser.addArgument("-o", "--output")
                .help("Output directory");
        parser.addArgument("-c", "--convention")
                .choices("IDENTITY", "UPPER_CAMEL_CASE", "UPPER_CAMEL_CASE_WITH_SPACES",
                        "LOWER_CASE_WITH_UNDERSCORES", "LOWER_CASE_WITH_DASHES", "LOWER_CASE_WITH_DOTS")
                .help("Field naming convention");
        Namespace ns = null;
        if (args.length < 3) {
            parser.printHelp();
            System.exit(0);
        }

        try {
            ns = parser.parseArgs(args);
        } catch (ArgumentParserException e) {
            parser.handleError(e);
            System.exit(1);
        }

        var input = ns.getString("input");
        var output = ns.getString("output");
        var nc = ns.getString("convention");
        var nameConvention = FieldNamingPolicy.valueOf(nc);

        new File(output).mkdirs();

        Files.list(Path.of(input)).forEach(file->{
            var fileName = file.getFileName().toString();
            var outputFile = Path.of(output, file.getFileName().toString()).toString();
            try(var reader = new BufferedReader(new FileReader(file.toAbsolutePath().toString()));
                var writer = new PrintWriter(new FileWriter(outputFile))) {

                var gson = new GsonBuilder()
                        .setPrettyPrinting()
                        .create();
                var root = gson.fromJson(reader, JsonElement.class);

                var converted = convert(root, nameConvention);

                String str = gson.toJson(converted);
                writer.write(str);
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        });
    }

    private static JsonElement convert(JsonElement src,FieldNamingPolicy nameConvention) {
        JsonElement ret;
        if (src.isJsonObject()){
            var jo = new JsonObject();
            var srcJo = src.getAsJsonObject();
            Set<Map.Entry<String, JsonElement>> es = srcJo.entrySet();
            for (Map.Entry<String, JsonElement> en : es) {
                jo.add(translateName(nameConvention, en.getKey()),convert(en.getValue(), nameConvention));
            }
            ret = jo;
        }else if(src.isJsonArray()){
            var array = new JsonArray();
            JsonArray ja = src.getAsJsonArray();
            if (null != ja) {
                for (JsonElement ae : ja) {
                    array.add(convert(ae, nameConvention));
                }
            }
            ret = array;
        }else if(src.isJsonPrimitive()){
            ret = src.deepCopy();
        }else{
            ret = JsonNull.INSTANCE;
        }

        return ret;
    }

    static String translateName(FieldNamingPolicy policy, String name){
        switch(policy){
            case IDENTITY:
                return name;
            case UPPER_CAMEL_CASE:
                return upperCaseFirstLetter(name);
            case UPPER_CAMEL_CASE_WITH_SPACES:
                return upperCaseFirstLetter(separateCamelCase(name, " "));
            case LOWER_CASE_WITH_UNDERSCORES :
                return separateCamelCase(name, "_").toLowerCase(Locale.ENGLISH);
            case LOWER_CASE_WITH_DASHES :
                return separateCamelCase(name, "-").toLowerCase(Locale.ENGLISH);
            case LOWER_CASE_WITH_DOTS:
                return separateCamelCase(name, ".").toLowerCase(Locale.ENGLISH);
            default:
                throw new UnsupportedOperationException("Naming policy is not supported");
        }
    }

    static String separateCamelCase(String name, String separator) {
        StringBuilder translation = new StringBuilder();
        int i = 0;

        for(int length = name.length(); i < length; ++i) {
            char character = name.charAt(i);
            if (Character.isUpperCase(character) && translation.length() != 0) {
                translation.append(separator);
            }

            translation.append(character);
        }

        return translation.toString();
    }

    static String upperCaseFirstLetter(String name) {
        int firstLetterIndex = 0;

        for(int limit = name.length() - 1; !Character.isLetter(name.charAt(firstLetterIndex)) && firstLetterIndex < limit; ++firstLetterIndex) {
        }

        char firstLetter = name.charAt(firstLetterIndex);
        if (Character.isUpperCase(firstLetter)) {
            return name;
        } else {
            char uppercased = Character.toUpperCase(firstLetter);
            return firstLetterIndex == 0 ? uppercased + name.substring(1) : name.substring(0, firstLetterIndex) + uppercased + name.substring(firstLetterIndex + 1);
        }
    }
}
