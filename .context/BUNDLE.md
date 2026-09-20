This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.ai/mcp/mcp.json
.ai/mcp/mcp.json-ollama
.coveragerc.toml
.gitignore
.repomixignore
CHANGELOG.md
CLAUDE.md
CONTRIBUTING.md
LICENSE
pyproject.toml
pytest-example.md
README.md
repomix.config.json
requirements.txt
scripts/test_client.py
scripts/test-mcp.py
src/mcp_project_context_server/__init__.py
src/mcp_project_context_server/__main__.py
src/mcp_project_context_server/exceptions.py
src/mcp_project_context_server/helpers/__init__.py
src/mcp_project_context_server/helpers/context_files.py
src/mcp_project_context_server/helpers/context.py
src/mcp_project_context_server/helpers/logs.py
src/mcp_project_context_server/helpers/sections.py
src/mcp_project_context_server/indexing/__init__.py
src/mcp_project_context_server/indexing/indexer.py
src/mcp_project_context_server/integrations/__init__.py
src/mcp_project_context_server/integrations/embeddings/__init__.py
src/mcp_project_context_server/integrations/embeddings/base.py
src/mcp_project_context_server/integrations/embeddings/cohere/__init__.py
src/mcp_project_context_server/integrations/embeddings/cohere/client.py
src/mcp_project_context_server/integrations/embeddings/google/__init__.py
src/mcp_project_context_server/integrations/embeddings/google/client.py
src/mcp_project_context_server/integrations/embeddings/ollama/__init__.py
src/mcp_project_context_server/integrations/embeddings/ollama/client.py
src/mcp_project_context_server/integrations/embeddings/openai/__init__.py
src/mcp_project_context_server/integrations/embeddings/openai/client.py
src/mcp_project_context_server/integrations/embeddings/registry.py
src/mcp_project_context_server/integrations/embeddings/vertexai/__init__.py
src/mcp_project_context_server/integrations/embeddings/vertexai/client.py
src/mcp_project_context_server/integrations/embeddings/voyage/__init__.py
src/mcp_project_context_server/integrations/embeddings/voyage/client.py
src/mcp_project_context_server/integrations/repository/__init__.py
src/mcp_project_context_server/integrations/repository/base.py
src/mcp_project_context_server/integrations/repository/gitea/__init__.py
src/mcp_project_context_server/integrations/repository/gitea/client.py
src/mcp_project_context_server/integrations/repository/github/__init__.py
src/mcp_project_context_server/integrations/repository/github/client.py
src/mcp_project_context_server/integrations/repository/gitlab/__init__.py
src/mcp_project_context_server/integrations/repository/gitlab/client.py
src/mcp_project_context_server/integrations/repository/local/__init__.py
src/mcp_project_context_server/integrations/repository/local/client.py
src/mcp_project_context_server/integrations/repository/registry.py
src/mcp_project_context_server/integrations/vectorstore/__init__.py
src/mcp_project_context_server/integrations/vectorstore/base.py
src/mcp_project_context_server/integrations/vectorstore/chroma_http/__init__.py
src/mcp_project_context_server/integrations/vectorstore/chroma_http/client.py
src/mcp_project_context_server/integrations/vectorstore/chroma_local/__init__.py
src/mcp_project_context_server/integrations/vectorstore/chroma_local/client.py
src/mcp_project_context_server/integrations/vectorstore/gcp_vector_search/__init__.py
src/mcp_project_context_server/integrations/vectorstore/gcp_vector_search/client.py
src/mcp_project_context_server/integrations/vectorstore/pgvector/__init__.py
src/mcp_project_context_server/integrations/vectorstore/pgvector/client.py
src/mcp_project_context_server/integrations/vectorstore/registry.py
src/mcp_project_context_server/server.py
src/mcp_project_context_server/tools/__init__.py
src/mcp_project_context_server/tools/find_latest_session_file.py
src/mcp_project_context_server/tools/index_context.py
src/mcp_project_context_server/tools/list_repositories.py
src/mcp_project_context_server/tools/load_context_files.py
src/mcp_project_context_server/tools/reload_active_context_file.py
src/mcp_project_context_server/tools/save_session.py
src/mcp_project_context_server/tools/search_adr_index.py
src/mcp_project_context_server/tools/search_context_index.py
src/mcp_project_context_server/tools/search_session_files.py
src/mcp_project_context_server/tools/search_shared.py
src/mcp_project_context_server/transport/__init__.py
src/mcp_project_context_server/transport/sse.py
src/mcp_project_context_server/transport/stdio.py
test.main.kts
```

# Files

## File: .ai/mcp/mcp.json
````json
{
  "mcpServers": {
    "project-context": {
      "command": "C:\\Users\\drahk\\python\\mcp-project-context-server-runtime\\Scripts\\python.exe",
      "args": [
        "-m",
        "mcp_project_context_server"
      ],
      "env": {
        "EMBED_PROVIDER": "voyage",
        "VOYAGE_EMBED_MODEL": "nomic-embed-text",
        "VOYAGE_API_KEY": "pa-8Xw0NlIjFlpbeydw79JJ-n2QDn3EJAevkw6LXaEwQhL",
        "CHROMA_DIR": "~/.mcp-data/Projects/mcp-project-context-server/chroma",
        "VIRTUAL_ENV": "C:/Users/drahk/python/mcp-project-context-server-runtime",
        "PATH": "%VIRTUAL_ENV%\\Scripts;%PATH%"
      }
    }
  }
}
````

## File: .ai/mcp/mcp.json-ollama
````
{
  "mcpServers": {
    "project-context": {
      "command": "C:\\Users\\drahk\\DMPProjects\\mcp-project-context-server\\.pcs-venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "mcp_project_context_server"
      ],
      "env": {
        "OLLAMA_HOST": "http://10.1.10.138:11434",
        "EMBED_PROVIDER": "ollama",
        "EMBED_MODEL": "nomic-embed-text",
        "CHROMA_DIR": "~/.mcp-data/Projects/mcp-project-context-server/chroma",
        "VIRTUAL_ENV": "C:\\Users\\drahk\\DMPProjects\\mcp-project-context-server\\.pcs-venv",
        "PATH": "%VIRTUAL_ENV%\\Scripts;%PATH%"
      }
    }
  }
}
````

## File: test.main.kts
````
#!/usr/bin/env kotlin

// Check if the user forgot to provide an argument
if (args.isEmpty()) {
    println("Error: Please enter the text you want to print.")
    System.exit(1)
}

// Retrieve the first argument
val inputText = args[0]

println("Your argument was: $inputText")
````

## File: .repomixignore
````
# Add patterns to ignore here, one per line
# Example:
# *.log
# tmp/
/src/*.egg-info/
/.benchmarks/
/.context/
/.git/
/.github/
/.idea/
/.tox/
/.vscode/
/.venv/
/.*venv/
/tests/
/dist/
/build/
/docs/

.claude/
.env*
.converage
*.ini
junit.xml
qodana.yaml
*.sav
````

## File: LICENSE
````
GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU Affero General Public License is a free, copyleft license for
software and other kinds of works, specifically designed to ensure
cooperation with the community in the case of network server software.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
our General Public Licenses are intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  Developers that use our General Public Licenses protect your rights
with two steps: (1) assert copyright on the software, and (2) offer
you this License which gives you legal permission to copy, distribute
and/or modify the software.

  A secondary benefit of defending all users' freedom is that
improvements made in alternate versions of the program, if they
receive widespread use, become available for other developers to
incorporate.  Many developers of free software are heartened and
encouraged by the resulting cooperation.  However, in the case of
software used on network servers, this result may fail to come about.
The GNU General Public License permits making a modified version and
letting the public access it on a server without ever releasing its
source code to the public.

  The GNU Affero General Public License is designed specifically to
ensure that, in such cases, the modified source code becomes available
to the community.  It requires the operator of a network server to
provide the source code of the modified version running there to the
users of that server.  Therefore, public use of a modified version, on
a publicly accessible server, gives the public access to the source
code of the modified version.

  An older license, called the Affero General Public License and
published by Affero, was designed to accomplish similar goals.  This is
a different license, not a version of the Affero GPL, but Affero has
released a new version of the Affero GPL which permits relicensing under
this license.

  The precise terms and conditions for copying, distribution and
modification follow.

                       TERMS AND CONDITIONS

  0. Definitions.

  "This License" refers to version 3 of the GNU Affero General Public License.

  "Copyright" also means copyright-like laws that apply to other kinds of
works, such as semiconductor masks.

  "The Program" refers to any copyrightable work licensed under this
License.  Each licensee is addressed as "you".  "Licensees" and
"recipients" may be individuals or organizations.

  To "modify" a work means to copy from or adapt all or part of the work
in a fashion requiring copyright permission, other than the making of an
exact copy.  The resulting work is called a "modified version" of the
earlier work or a work "based on" the earlier work.

  A "covered work" means either the unmodified Program or a work based
on the Program.

  To "propagate" a work means to do anything with it that, without
permission, would make you directly or secondarily liable for
infringement under applicable copyright law, except executing it on a
computer or modifying a private copy.  Propagation includes copying,
distribution (with or without modification), making available to the
public, and in some countries other activities as well.

  To "convey" a work means any kind of propagation that enables other
parties to make or receive copies.  Mere interaction with a user through
a computer network, with no transfer of a copy, is not conveying.

  An interactive user interface displays "Appropriate Legal Notices"
to the extent that it includes a convenient and prominently visible
feature that (1) displays an appropriate copyright notice, and (2)
tells the user that there is no warranty for the work (except to the
extent that warranties are provided), that licensees may convey the
work under this License, and how to view a copy of this License.  If
the interface presents a list of user commands or options, such as a
menu, a prominent item in the list meets this criterion.

  1. Source Code.

  The "source code" for a work means the preferred form of the work
for making modifications to it.  "Object code" means any non-source
form of a work.

  A "Standard Interface" means an interface that either is an official
standard defined by a recognized standards body, or, in the case of
interfaces specified for a particular programming language, one that
is widely used among developers working in that language.

  The "System Libraries" of an executable work include anything, other
than the work as a whole, that (a) is included in the normal form of
packaging a Major Component, but which is not part of that Major
Component, and (b) serves only to enable use of the work with that
Major Component, or to implement a Standard Interface for which an
implementation is available to the public in source code form.  A
"Major Component", in this context, means a major essential component
(kernel, window system, and so on) of the specific operating system
(if any) on which the executable work runs, or a compiler used to
produce the work, or an object code interpreter used to run it.

  The "Corresponding Source" for a work in object code form means all
the source code needed to generate, install, and (for an executable
work) run the object code and to modify the work, including scripts to
control those activities.  However, it does not include the work's
System Libraries, or general-purpose tools or generally available free
programs which are used unmodified in performing those activities but
which are not part of the work.  For example, Corresponding Source
includes interface definition files associated with source files for
the work, and the source code for shared libraries and dynamically
linked subprograms that the work is specifically designed to require,
such as by intimate data communication or control flow between those
subprograms and other parts of the work.

  The Corresponding Source need not include anything that users
can regenerate automatically from other parts of the Corresponding
Source.

  The Corresponding Source for a work in source code form is that
same work.

  2. Basic Permissions.

  All rights granted under this License are granted for the term of
copyright on the Program, and are irrevocable provided the stated
conditions are met.  This License explicitly affirms your unlimited
permission to run the unmodified Program.  The output from running a
covered work is covered by this License only if the output, given its
content, constitutes a covered work.  This License acknowledges your
rights of fair use or other equivalent, as provided by copyright law.

  You may make, run and propagate covered works that you do not
convey, without conditions so long as your license otherwise remains
in force.  You may convey covered works to others for the sole purpose
of having them make modifications exclusively for you, or provide you
with facilities for running those works, provided that you comply with
the terms of this License in conveying all material for which you do
not control copyright.  Those thus making or running the covered works
for you must do so exclusively on your behalf, under your direction
and control, on terms that prohibit them from making any copies of
your copyrighted material outside their relationship with you.

  Conveying under any other circumstances is permitted solely under
the conditions stated below.  Sublicensing is not allowed; section 10
makes it unnecessary.

  3. Protecting Users' Legal Rights From Anti-Circumvention Law.

  No covered work shall be deemed part of an effective technological
measure under any applicable law fulfilling obligations under article
11 of the WIPO copyright treaty adopted on 20 December 1996, or
similar laws prohibiting or restricting circumvention of such
measures.

  When you convey a covered work, you waive any legal power to forbid
circumvention of technological measures to the extent such circumvention
is effected by exercising rights under this License with respect to
the covered work, and you disclaim any intention to limit operation or
modification of the work as a means of enforcing, against the work's
users, your or third parties' legal rights to forbid circumvention of
technological measures.

  4. Conveying Verbatim Copies.

  You may convey verbatim copies of the Program's source code as you
receive it, in any medium, provided that you conspicuously and
appropriately publish on each copy an appropriate copyright notice;
keep intact all notices stating that this License and any
non-permissive terms added in accord with section 7 apply to the code;
keep intact all notices of the absence of any warranty; and give all
recipients a copy of this License along with the Program.

  You may charge any price or no price for each copy that you convey,
and you may offer support or warranty protection for a fee.

  5. Conveying Modified Source Versions.

  You may convey a work based on the Program, or the modifications to
produce it from the Program, in the form of source code under the
terms of section 4, provided that you also meet all of these conditions:

    a) The work must carry prominent notices stating that you modified
    it, and giving a relevant date.

    b) The work must carry prominent notices stating that it is
    released under this License and any conditions added under section
    7.  This requirement modifies the requirement in section 4 to
    "keep intact all notices".

    c) You must license the entire work, as a whole, under this
    License to anyone who comes into possession of a copy.  This
    License will therefore apply, along with any applicable section 7
    additional terms, to the whole of the work, and all its parts,
    regardless of how they are packaged.  This License gives no
    permission to license the work in any other way, but it does not
    invalidate such permission if you have separately received it.

    d) If the work has interactive user interfaces, each must display
    Appropriate Legal Notices; however, if the Program has interactive
    interfaces that do not display Appropriate Legal Notices, your
    work need not make them do so.

  A compilation of a covered work with other separate and independent
works, which are not by their nature extensions of the covered work,
and which are not combined with it such as to form a larger program,
in or on a volume of a storage or distribution medium, is called an
"aggregate" if the compilation and its resulting copyright are not
used to limit the access or legal rights of the compilation's users
beyond what the individual works permit.  Inclusion of a covered work
in an aggregate does not cause this License to apply to the other
parts of the aggregate.

  6. Conveying Non-Source Forms.

  You may convey a covered work in object code form under the terms
of sections 4 and 5, provided that you also convey the
machine-readable Corresponding Source under the terms of this License,
in one of these ways:

    a) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by the
    Corresponding Source fixed on a durable physical medium
    customarily used for software interchange.

    b) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by a
    written offer, valid for at least three years and valid for as
    long as you offer spare parts or customer support for that product
    model, to give anyone who possesses the object code either (1) a
    copy of the Corresponding Source for all the software in the
    product that is covered by this License, on a durable physical
    medium customarily used for software interchange, for a price no
    more than your reasonable cost of physically performing this
    conveying of source, or (2) access to copy the
    Corresponding Source from a network server at no charge.

    c) Convey individual copies of the object code with a copy of the
    written offer to provide the Corresponding Source.  This
    alternative is allowed only occasionally and noncommercially, and
    only if you received the object code with such an offer, in accord
    with subsection 6b.

    d) Convey the object code by offering access from a designated
    place (gratis or for a charge), and offer equivalent access to the
    Corresponding Source in the same way through the same place at no
    further charge.  You need not require recipients to copy the
    Corresponding Source along with the object code.  If the place to
    copy the object code is a network server, the Corresponding Source
    may be on a different server (operated by you or a third party)
    that supports equivalent copying facilities, provided you maintain
    clear directions next to the object code saying where to find the
    Corresponding Source.  Regardless of what server hosts the
    Corresponding Source, you remain obligated to ensure that it is
    available for as long as needed to satisfy these requirements.

    e) Convey the object code using peer-to-peer transmission, provided
    you inform other peers where the object code and Corresponding
    Source of the work are being offered to the general public at no
    charge under subsection 6d.

  A separable portion of the object code, whose source code is excluded
from the Corresponding Source as a System Library, need not be
included in conveying the object code work.

  A "User Product" is either (1) a "consumer product", which means any
tangible personal property which is normally used for personal, family,
or household purposes, or (2) anything designed or sold for incorporation
into a dwelling.  In determining whether a product is a consumer product,
doubtful cases shall be resolved in favor of coverage.  For a particular
product received by a particular user, "normally used" refers to a
typical or common use of that class of product, regardless of the status
of the particular user or of the way in which the particular user
actually uses, or expects or is expected to use, the product.  A product
is a consumer product regardless of whether the product has substantial
commercial, industrial or non-consumer uses, unless such uses represent
the only significant mode of use of the product.

  "Installation Information" for a User Product means any methods,
procedures, authorization keys, or other information required to install
and execute modified versions of a covered work in that User Product from
a modified version of its Corresponding Source.  The information must
suffice to ensure that the continued functioning of the modified object
code is in no case prevented or interfered with solely because
modification has been made.

  If you convey an object code work under this section in, or with, or
specifically for use in, a User Product, and the conveying occurs as
part of a transaction in which the right of possession and use of the
User Product is transferred to the recipient in perpetuity or for a
fixed term (regardless of how the transaction is characterized), the
Corresponding Source conveyed under this section must be accompanied
by the Installation Information.  But this requirement does not apply
if neither you nor any third party retains the ability to install
modified object code on the User Product (for example, the work has
been installed in ROM).

  The requirement to provide Installation Information does not include a
requirement to continue to provide support service, warranty, or updates
for a work that has been modified or installed by the recipient, or for
the User Product in which it has been modified or installed.  Access to a
network may be denied when the modification itself materially and
adversely affects the operation of the network or violates the rules and
protocols for communication across the network.

  Corresponding Source conveyed, and Installation Information provided,
in accord with this section must be in a format that is publicly
documented (and with an implementation available to the public in
source code form), and must require no special password or key for
unpacking, reading or copying.

  7. Additional Terms.

  "Additional permissions" are terms that supplement the terms of this
License by making exceptions from one or more of its conditions.
Additional permissions that are applicable to the entire Program shall
be treated as though they were included in this License, to the extent
that they are valid under applicable law.  If additional permissions
apply only to part of the Program, that part may be used separately
under those permissions, but the entire Program remains governed by
this License without regard to the additional permissions.

  When you convey a copy of a covered work, you may at your option
remove any additional permissions from that copy, or from any part of
it.  (Additional permissions may be written to require their own
removal in certain cases when you modify the work.)  You may place
additional permissions on material, added by you to a covered work,
for which you have or can give appropriate copyright permission.

  Notwithstanding any other provision of this License, for material you
add to a covered work, you may (if authorized by the copyright holders of
that material) supplement the terms of this License with terms:

    a) Disclaiming warranty or limiting liability differently from the
    terms of sections 15 and 16 of this License; or

    b) Requiring preservation of specified reasonable legal notices or
    author attributions in that material or in the Appropriate Legal
    Notices displayed by works containing it; or

    c) Prohibiting misrepresentation of the origin of that material, or
    requiring that modified versions of such material be marked in
    reasonable ways as different from the original version; or

    d) Limiting the use for publicity purposes of names of licensors or
    authors of the material; or

    e) Declining to grant rights under trademark law for use of some
    trade names, trademarks, or service marks; or

    f) Requiring indemnification of licensors and authors of that
    material by anyone who conveys the material (or modified versions of
    it) with contractual assumptions of liability to the recipient, for
    any liability that these contractual assumptions directly impose on
    those licensors and authors.

  All other non-permissive additional terms are considered "further
restrictions" within the meaning of section 10.  If the Program as you
received it, or any part of it, contains a notice stating that it is
governed by this License along with a term that is a further
restriction, you may remove that term.  If a license document contains
a further restriction but permits relicensing or conveying under this
License, you may add to a covered work material governed by the terms
of that license document, provided that the further restriction does
not survive such relicensing or conveying.

  If you add terms to a covered work in accord with this section, you
must place, in the relevant source files, a statement of the
additional terms that apply to those files, or a notice indicating
where to find the applicable terms.

  Additional terms, permissive or non-permissive, may be stated in the
form of a separately written license, or stated as exceptions;
the above requirements apply either way.

  8. Termination.

  You may not propagate or modify a covered work except as expressly
provided under this License.  Any attempt otherwise to propagate or
modify it is void, and will automatically terminate your rights under
this License (including any patent licenses granted under the third
paragraph of section 11).

  However, if you cease all violation of this License, then your
license from a particular copyright holder is reinstated (a)
provisionally, unless and until the copyright holder explicitly and
finally terminates your license, and (b) permanently, if the copyright
holder fails to notify you of the violation by some reasonable means
prior to 60 days after the cessation.

  Moreover, your license from a particular copyright holder is
reinstated permanently if the copyright holder notifies you of the
violation by some reasonable means, this is the first time you have
received notice of violation of this License (for any work) from that
copyright holder, and you cure the violation prior to 30 days after
your receipt of the notice.

  Termination of your rights under this section does not terminate the
licenses of parties who have received copies or rights from you under
this License.  If your rights have been terminated and not permanently
reinstated, you do not qualify to receive new licenses for the same
material under section 10.

  9. Acceptance Not Required for Having Copies.

  You are not required to accept this License in order to receive or
run a copy of the Program.  Ancillary propagation of a covered work
occurring solely as a consequence of using peer-to-peer transmission
to receive a copy likewise does not require acceptance.  However,
nothing other than this License grants you permission to propagate or
modify any covered work.  These actions infringe copyright if you do
not accept this License.  Therefore, by modifying or propagating a
covered work, you indicate your acceptance of this License to do so.

  10. Automatic Licensing of Downstream Recipients.

  Each time you convey a covered work, the recipient automatically
receives a license from the original licensors, to run, modify and
propagate that work, subject to this License.  You are not responsible
for enforcing compliance by third parties with this License.

  An "entity transaction" is a transaction transferring control of an
organization, or substantially all assets of one, or subdividing an
organization, or merging organizations.  If propagation of a covered
work results from an entity transaction, each party to that
transaction who receives a copy of the work also receives whatever
licenses to the work the party's predecessor in interest had or could
give under the previous paragraph, plus a right to possession of the
Corresponding Source of the work from the predecessor in interest, if
the predecessor has it or can get it with reasonable efforts.

  You may not impose any further restrictions on the exercise of the
rights granted or affirmed under this License.  For example, you may
not impose a license fee, royalty, or other charge for exercise of
rights granted under this License, and you may not initiate litigation
(including a cross-claim or counterclaim in a lawsuit) alleging that
any patent claim is infringed by making, using, selling, offering for
sale, or importing the Program or any portion of it.

  11. Patents.

  A "contributor" is a copyright holder who authorizes use under this
License of the Program or a work on which the Program is based.  The
work thus licensed is called the contributor's "contributor version".

  A contributor's "essential patent claims" are all patent claims
owned or controlled by the contributor, whether already acquired or
hereafter acquired, that would be infringed by some manner, permitted
by this License, of making, using, or selling its contributor version,
but do not include claims that would be infringed only as a
consequence of further modification of the contributor version.  For
purposes of this definition, "control" includes the right to grant
patent sublicenses in a manner consistent with the requirements of
this License.

  Each contributor grants you a non-exclusive, worldwide, royalty-free
patent license under the contributor's essential patent claims, to
make, use, sell, offer for sale, import and otherwise run, modify and
propagate the contents of its contributor version.

  In the following three paragraphs, a "patent license" is any express
agreement or commitment, however denominated, not to enforce a patent
(such as an express permission to practice a patent or covenant not to
sue for patent infringement).  To "grant" such a patent license to a
party means to make such an agreement or commitment not to enforce a
patent against the party.

  If you convey a covered work, knowingly relying on a patent license,
and the Corresponding Source of the work is not available for anyone
to copy, free of charge and under the terms of this License, through a
publicly available network server or other readily accessible means,
then you must either (1) cause the Corresponding Source to be so
available, or (2) arrange to deprive yourself of the benefit of the
patent license for this particular work, or (3) arrange, in a manner
consistent with the requirements of this License, to extend the patent
license to downstream recipients.  "Knowingly relying" means you have
actual knowledge that, but for the patent license, your conveying the
covered work in a country, or your recipient's use of the covered work
in a country, would infringe one or more identifiable patents in that
country that you have reason to believe are valid.

  If, pursuant to or in connection with a single transaction or
arrangement, you convey, or propagate by procuring conveyance of, a
covered work, and grant a patent license to some of the parties
receiving the covered work authorizing them to use, propagate, modify
or convey a specific copy of the covered work, then the patent license
you grant is automatically extended to all recipients of the covered
work and works based on it.

  A patent license is "discriminatory" if it does not include within
the scope of its coverage, prohibits the exercise of, or is
conditioned on the non-exercise of one or more of the rights that are
specifically granted under this License.  You may not convey a covered
work if you are a party to an arrangement with a third party that is
in the business of distributing software, under which you make payment
to the third party based on the extent of your activity of conveying
the work, and under which the third party grants, to any of the
parties who would receive the covered work from you, a discriminatory
patent license (a) in connection with copies of the covered work
conveyed by you (or copies made from those copies), or (b) primarily
for and in connection with specific products or compilations that
contain the covered work, unless you entered into that arrangement,
or that patent license was granted, prior to 28 March 2007.

  Nothing in this License shall be construed as excluding or limiting
any implied license or other defenses to infringement that may
otherwise be available to you under applicable patent law.

  12. No Surrender of Others' Freedom.

  If conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot convey a
covered work so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you may
not convey it at all.  For example, if you agree to terms that obligate you
to collect a royalty for further conveying from those to whom you convey
the Program, the only way you could satisfy both those terms and this
License would be to refrain entirely from conveying the Program.

  13. Remote Network Interaction; Use with the GNU General Public License.

  Notwithstanding any other provision of this License, if you modify the
Program, your modified version must prominently offer all users
interacting with it remotely through a computer network (if your version
supports such interaction) an opportunity to receive the Corresponding
Source of your version by providing access to the Corresponding Source
from a network server at no charge, through some standard or customary
means of facilitating copying of software.  This Corresponding Source
shall include the Corresponding Source for any work covered by version 3
of the GNU General Public License that is incorporated pursuant to the
following paragraph.

  Notwithstanding any other provision of this License, you have
permission to link or combine any covered work with a work licensed
under version 3 of the GNU General Public License into a single
combined work, and to convey the resulting work.  The terms of this
License will continue to apply to the part which is the covered work,
but the work with which it is combined will remain governed by version
3 of the GNU General Public License.

  14. Revised Versions of this License.

  The Free Software Foundation may publish revised and/or new versions of
the GNU Affero General Public License from time to time.  Such new versions
will be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

  Each version is given a distinguishing version number.  If the
Program specifies that a certain numbered version of the GNU Affero General
Public License "or any later version" applies to it, you have the
option of following the terms and conditions either of that numbered
version or of any later version published by the Free Software
Foundation.  If the Program does not specify a version number of the
GNU Affero General Public License, you may choose any version ever published
by the Free Software Foundation.

  If the Program specifies that a proxy can decide which future
versions of the GNU Affero General Public License can be used, that proxy's
public statement of acceptance of a version permanently authorizes you
to choose that version for the Program.

  Later license versions may give you additional or different
permissions.  However, no additional obligations are imposed on any
author or copyright holder as a result of your choosing to follow a
later version.

  15. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  16. Limitation of Liability.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
SUCH DAMAGES.

  17. Interpretation of Sections 15 and 16.

  If the disclaimer of warranty and limitation of liability provided
above cannot be given local legal effect according to their terms,
reviewing courts shall apply local law that most closely approximates
an absolute waiver of all civil liability in connection with the
Program, unless a warranty or assumption of liability accompanies a
copy of the Program in return for a fee.

                     END OF TERMS AND CONDITIONS

            How to Apply These Terms to Your New Programs

  If you develop a new program, and you want it to be of the greatest
possible use to the public, the best way to achieve this is to make it
free software which everyone can redistribute and change under these terms.

  To do so, attach the following notices to the program.  It is safest
to attach them to the start of each source file to most effectively
state the exclusion of warranty; and each file should have at least
the "copyright" line and a pointer to where the full notice is found.

    <one line to give the program's name and a brief idea of what it does.>
    Copyright (C) <year>  <name of author>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

Also add information on how to contact you by electronic and paper mail.

  If your software can interact with users remotely through a computer
network, you should also make sure that it provides a way for users to
get its source.  For example, if your program is a web application, its
interface could display a "Source" link that leads users to an archive
of the code.  There are many ways you could offer source, and different
solutions will be better for different programs; see section 13 for the
specific requirements.

  You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU AGPL, see
<https://www.gnu.org/licenses/>.
````

## File: pytest-example.md
````markdown
# MCP Server Integration Testing with Python

Integration testing an MCP server means writing tests that actually speak the MCP protocol
over stdio — booting your real server process and exercising it end-to-end. This sits between
unit tests (pure Python, no protocol) and manual testing in Claude Desktop.

---

## Prerequisites

```bash
pip install mcp pytest pytest-asyncio
```

Your `pytest.ini` (or `pyproject.toml`) should enable async mode:

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

---

## Core Pattern

Every integration test follows the same structure:

1. Define `StdioServerParameters` pointing at your server process
2. Open a `stdio_client` context — this spawns the process
3. Open a `ClientSession` context — this handles the MCP handshake
4. Call `session.initialize()`
5. Make assertions

```python
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.fixture
def server_params():
    return StdioServerParameters(
        command="python",
        args=["my_server.py"],
        # Optional: pass env vars to the server process
        env={"MY_API_KEY": "test-key"}
    )


async def test_example(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # your assertions here
```

---

## Testing Tools

### List available tools

```python
async def test_tools_are_registered(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.list_tools()
            tool_names = [t.name for t in result.tools]

            assert "get_weather" in tool_names
            assert "search_docs" in tool_names
```

### Call a tool and inspect output

```python
async def test_get_weather_returns_city(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("get_weather", {"city": "Chicago"})

            # result.content is a list of content blocks
            assert len(result.content) > 0
            assert result.content[0].type == "text"
            assert "Chicago" in result.content[0].text
```

### Test tool error handling

```python
async def test_missing_argument_raises_error(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("get_weather", {})  # missing 'city'

            # MCP surfaces errors as is_error=True, not exceptions
            assert result.is_error is True
```

---

## Testing Resources

### List available resources

```python
async def test_resources_are_registered(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.list_resources()
            uris = [r.uri for r in result.resources]

            assert "file:///config" in uris
```

### Read a resource

```python
async def test_read_config_resource(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.read_resource("file:///config")

            assert len(result.contents) > 0
            # Text resources have a .text attribute
            assert "version" in result.contents[0].text
```

---

## Testing Prompts

### List available prompts

```python
async def test_prompts_are_registered(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.list_prompts()
            prompt_names = [p.name for p in result.prompts]

            assert "summarise" in prompt_names
```

### Get a prompt with arguments

```python
async def test_summarise_prompt(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.get_prompt(
                "summarise",
                {"text": "The quick brown fox jumps over the lazy dog."}
            )

            # result.messages is a list of PromptMessage objects
            assert len(result.messages) > 0
            assert result.messages[0].role == "user"
```

---

## Shared Fixture (DRY)

If you have many tests, avoid repeating the context manager boilerplate with a session fixture:

```python
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.fixture
def server_params():
    return StdioServerParameters(command="python", args=["my_server.py"])


@pytest.fixture
async def session(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()
            yield s  # tests run here; both contexts stay open


# Tests now just receive `session` directly
async def test_tools(session):
    result = await session.list_tools()
    assert len(result.tools) > 0


async def test_weather(session):
    result = await session.call_tool("get_weather", {"city": "Chicago"})
    assert "Chicago" in result.content[0].text
```

> **Note:** Each test gets a **fresh server process** because the fixture spins up a new
> `stdio_client` per test. If startup is slow, scope the fixture to `"module"` or `"session"`,
> but be aware that state may bleed between tests.

---

## Running the Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run a single test
pytest tests/integration/test_tools.py::test_get_weather_returns_city -v

# Run with stdout visible (useful when debugging server logs)
pytest tests/integration/ -v -s
```

---

## Tips

- **Keep unit tests separate** — integration tests are slower because they spawn a real process.
  Put them in a dedicated `tests/integration/` directory and run them separately in CI.

- **Server logs go to stderr** — MCP servers write logs to stderr so they don't interfere with
  the stdio transport. Use `-s` with pytest to see them, or redirect: `args=["my_server.py"],
  env={"LOG_LEVEL": "DEBUG"}`.

- **`result.is_error` vs exceptions** — the MCP client does not raise Python exceptions for
  tool errors. Instead, `result.is_error` is `True` and the error message is in
  `result.content[0].text`. Always check `is_error` when testing failure paths.

- **`initialize()` is mandatory** — skipping it will cause all subsequent calls to hang or fail.
  Always call it right after opening the session.
````

## File: repomix.config.json
````json
{
  "$schema": "https://repomix.com/schemas/latest/schema.json",
  "input": {
    "maxFileSize": 52428800
  },
  "output": {
    "filePath": ".context/BUNDLE.md",
    "style": "markdown",
    "parsableStyle": false,
    "fileSummary": true,
    "directoryStructure": true,
    "files": true,
    "removeComments": false,
    "removeEmptyLines": false,
    "compress": false,
    "topFilesLength": 5,
    "showLineNumbers": false,
    "copyToClipboard": false,
    "git": {
      "sortByChanges": true,
      "sortByChangesMaxCommits": 100,
      "includeDiffs": false
    }
  },
  "include": [],
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": []
  },
  "security": {
    "enableSecurityCheck": true
  },
  "tokenCount": {
    "encoding": "o200k_base"
  }
}
````

## File: scripts/test-mcp.py
````python
import argparse
import asyncio
import json
import os
import sys
from typing import Dict

# ==========================================
# CONFIGURATION
# ==========================================
# sys.executable automatically tracks the active virtualenv's Python binary
SERVER_COMMAND = [sys.executable, "-m", "mcp_project_context_server.__main__"]

# Set a massive buffer size (32 Megabytes) to handle giant project file contexts
STREAM_BUFFER_LIMIT = 32 * 1024 * 1024

# A real path on your system to bypass validation checks
TEST_PATH = r"C:/Users/drahk/DMPProjects/mcp-project-context-server"

# ==========================================
# TEST PAYLOADS
# ==========================================
TEST_PAYLOADS = {}

# ==========================================
# ARGUMENTS
# ==========================================

parser = argparse.ArgumentParser(description="Script for rendering output from the MCP server")
parser.add_argument("--tool", "-t", choices=list(TEST_PAYLOADS.keys()).append("all"), default="all")
parser.add_argument("--gh-org", "-o", type=str)
parser.add_argument("--details", "-d", action="store_true")
args = parser.parse_args()

TEST_PAYLOADS = {
    "search_context_index": {
        "name": "search_context_index",
        "arguments": {
            "project_path": TEST_PATH,
            "query": "architecture notes",
            "n_results": 2
        }
    },
    "search_adr_index": {
        "name": "search_adr_index",
        "arguments": {
            "project_path": TEST_PATH,
            "query": "architecture decisions",
            "n_results": 2
        }
    },
    "search_session_files": {
        "name": "search_session_files",
        "arguments": {
            "project_path": TEST_PATH,
            "query": "session summary",
            "n_results": 2
        }
    },
    "find_latest_session_file": {
        "name": "find_latest_session_file",
        "arguments": {"project_path": TEST_PATH}
    },
    "load_context_files": {
        "name": "load_context_files",
        "arguments": {"project_path": TEST_PATH, "files": ["project.md"]}
    },
    "reload_active_context_file": {
        "name": "reload_active_context_file",
        "arguments": {
            "project_path": TEST_PATH,
            "files": [{"path": "project.md", "known_sha512": "deadbeef"}]
        }
    },
    "save_session_summary": {
        "name": "save_session_summary",
        "arguments": {
            "project_path": TEST_PATH,
            "summary": "### Session\n- Upgraded script to handle massive JSON streams."
        }
    },
    "index_project_context": {
        "name": "index_project_context",
        "arguments": {"project_path": TEST_PATH}
    }
}

if args.gh_org:
    print(f"Listing repositories for organization: {args.gh_org}")
    TEST_PAYLOADS["list_repositories"] = {
        "name": "list_repositories",
        "arguments": {"org": f"{args.gh_org}"}
    }

async def read_response(reader):
    """Reads a single line/message from the server stdout safely on Windows."""
    try:
        line = await reader.readline()
        if not line:
            return None
        cleaned_line = line.decode('utf-8').strip()
        return json.loads(cleaned_line)
    except asyncio.LimitOverrunError as e:
        print(f"\n[CRITICAL ERROR]: Line exceeded the stream buffer! {e}")
        raise

async def send_request(writer, method, params, request_id):
    """Formats and sends a JSON-RPC request to the server."""
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params
    }
    raw_payload = json.dumps(payload) + "\n"
    writer.write(raw_payload.encode('utf-8'))
    await writer.drain()
    print(f"\n[CLIENT -> SERVER] Request Sent\n"
          f"    ID: {request_id}\n"
          f"    method: {method}\n"
          f"    params: {params}\n"
          )

async def send_notification(writer, method, params):
    """Sends a JSON-RPC notification (no ID, no response expected)."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params
    }
    raw_payload = json.dumps(payload) + "\n"
    writer.write(raw_payload.encode('utf-8'))
    await writer.drain()
    print(f"[CLIENT -> SERVER] Sent notification: {method}")

from typing import Any

def trunc_json_values(value: Any, details: bool, level: int = 0) -> Any:
    if isinstance(value, str):
        if len(value) > 1000 and not details:
            return f"{value[:200]} ... [TRUNCATED FOR TERMINAL READABILITY] ..."
        return value

    if isinstance(value, dict):
        return {
            key: trunc_json_values(item, details, level + 1)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            trunc_json_values(item, details, level + 1)
            for item in value
        ]

    return value

async def main():
    print(f"Starting MCP server via: {' '.join(SERVER_COMMAND)}")
    print(f"Applying StreamReader stream limit: {STREAM_BUFFER_LIMIT // (1024*1024)} MB")

    # CRITICAL FIX: Pass 'limit' argument directly to the executive wrapper
    process = await asyncio.create_subprocess_exec(
        *SERVER_COMMAND,
        env=os.environ,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=None,                  # Pushes raw execution exceptions directly to your screen
        limit=STREAM_BUFFER_LIMIT      # Overrides the default 64KB lock with 32MB
    )

    writer = process.stdin
    reader = process.stdout
    req_id = 1

    try:
        # Handshake Phase 1
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "mcp-test-harness", "version": "1.0.0"}
        }
        await send_request(writer, "initialize", init_params, req_id)

        init_resp = await read_response(reader)
        print(f"[SERVER -> CLIENT] Init Response received.")

        # Handshake Phase 2
        req_id += 1
        await send_notification(writer, "notifications/initialized", {})
        print("Handshake completed successfully!\n" + "="*50)

        # Loop and test every single schema definition
        payloads: Dict[str, str | Dict[str, str | Dict[str, str | int]]] = TEST_PAYLOADS if args.tool == "all" else {args.tool: TEST_PAYLOADS[args.tool]}
        for tool_name, tool in payloads.items():
            req_id += 1
            print(f"[SERVER -> CLIENT] Request for '{tool_name}':")
            tool_request = json.dumps(tool, indent=2)
            print(tool_request)

            await send_request(writer, "tools/call", tool, req_id)

            response = await read_response(reader)
            print(f"[SERVER -> CLIENT] Response for '{tool_name}':")

            if isinstance(response, dict):
                resp_str = json.dumps({key: trunc_json_values(value, args.details) for key, value in response.items()}, indent=2)
            else:
                print("No response.")
                break

            print(resp_str)
            print(f"Total Response Length: {len(resp_str)} characters.")
            print("-" * 50)

    except Exception as e:
        print(f"An error occurred during execution: {e}")
    finally:
        print("Closing server connection...")
        writer.close()
        await writer.wait_closed()
        process.terminate()
        await process.wait()
        print("Server process stopped.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
````

## File: src/mcp_project_context_server/exceptions.py
````python
"""Custom exception types shared across the server and its integrations."""


class EmbeddingError(Exception):
    """Raised when an embedding provider call fails."""
````

## File: src/mcp_project_context_server/helpers/context_files.py
````python
"""Shared helpers for loading, hashing, and listing individual .context/ files."""
import hashlib
import logging
from pathlib import Path

from mcp_project_context_server.helpers.context import find_context_dir, resolve_project_path
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider

logger = logging.getLogger(__name__)


def hash_content(content: str) -> str:
    """Compute the SHA-512 hex digest of *content*.

    :param content: (str) The file content to hash.
    :return: (str) The hex-encoded SHA-512 digest of *content*.
    """
    return hashlib.sha512(content.encode("utf-8")).hexdigest()


def format_tagged_file(path: str, sha512: str, content: str) -> str:
    """Format *content* as an XML-tagged context-file block.

    :param path: (str) The ``.context/``-relative path of the file.
    :param sha512: (str) The SHA-512 hex digest of *content*.
    :param content: (str) The file's contents.
    :return: (str) A ``<context-file path="..." sha512="...">`` tagged block.
    """
    return f'<context-file path="{path}" sha512="{sha512}">\n{content}\n</context-file>'


def _is_safe_relative_path(rel_path: str) -> bool:
    """Reject absolute paths and paths containing ``..`` segments.

    These tools are reachable over the ``sse`` transport where input is not
    necessarily trusted, so a requested path must stay within ``.context/``.
    """
    p = Path(rel_path)
    if p.is_absolute():
        return False
    return ".." not in p.parts


async def resolve_requested_files(project_path: str, rel_paths: list[str]) -> tuple[dict[str, str], list[str]]:
    """Resolve a list of ``.context/``-relative paths to their contents.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :param rel_paths: (list) POSIX-style paths relative to ``.context/``.
    :return: (tuple) A ``(found, missing)`` pair — ``found`` maps requested paths to
        their contents; ``missing`` lists requested paths that could not be
        resolved (not found on disk/remote, or rejected as unsafe).
    """
    logger.debug(f"Executing 'resolve_requested_files' with the argument rel_paths: {rel_paths}")
    safe_paths = [p for p in rel_paths if _is_safe_relative_path(p)]

    provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(project_path, provider.provider_name)
    found: dict[str, str] = {}

    if is_remote:
        try:
            files = await provider.fetch_context_files(resolved_path)
        except RepositoryError:
            files = {}
        found = {p: files[p] for p in safe_paths if p in files}
    else:
        context_dir = find_context_dir(resolved_path)
        if context_dir is not None:
            for p in safe_paths:
                candidate = context_dir / p
                if candidate.is_file():
                    found[p] = candidate.read_text(encoding="utf-8")

    missing = [p for p in rel_paths if p not in found]
    return found, missing


async def list_context_files(project_path: str, prefix: str) -> list[str]:
    """List sorted ``.context/``-relative markdown paths starting with *prefix*.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :param prefix: (str) A POSIX-style path prefix, e.g. ``"sessions/"``.
    :return: (list) Sorted relative paths (POSIX-style) starting with *prefix*.
    """
    provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(project_path, provider.provider_name)

    if is_remote:
        try:
            files = await provider.fetch_context_files(resolved_path)
        except RepositoryError:
            return []
        return sorted(k for k in files if k.startswith(prefix))

    context_dir = find_context_dir(resolved_path)
    if context_dir is None:
        return []

    all_paths = (m.relative_to(context_dir).as_posix() for m in context_dir.rglob("*.md"))
    return sorted(p for p in all_paths if p.startswith(prefix))
````

## File: src/mcp_project_context_server/helpers/logs.py
````python
import argparse
import logging
import sys
import uuid
from pathlib import Path


class ParseLogLevel(argparse.Action):
    """
    Collects repeated --log-level name=LEVEL flags into a dict.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        d = getattr(namespace, self.dest) or {}
        try:
            name, level = values.split("=", 1)
        except ValueError:
            raise argparse.ArgumentError(
                self, f"expected format name=LEVEL, got '{values}'"
            )
        d[name] = level
        setattr(namespace, self.dest, d)


def setup_logging(logger_levels: dict[str, int | str] | None = None):
    """
    Configure the root logger to log to stdout and to _LOG_PATH.

    logger_levels: optional dict of {"<library_name>": <log_level>}
        to override the level for specific loggers, e.g.
        {"urllib3": "WARNING", "botocore": logging.WARNING}
        Values can be int constants (logging.WARNING) or level
        name strings ("WARNING", "debug", etc. - case-insensitive).
    """
    _PROCESS_ID = uuid.uuid4().hex[:8]
    _LOG_PATH = Path.home() / ".mcp-data" / "logs" / f"project-context-server-{_PROCESS_ID}.log"


    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    file_handler = logging.FileHandler(_LOG_PATH, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    # Guard against duplicate handlers if setup_logging() runs more than once
    if not root.handlers:
        root.addHandler(file_handler)
        # root.addHandler(stream_handler)

    # --- Per-logger level overrides ---
    for name, level in (logger_levels or {}).items():
        if isinstance(level, str):
            level = level.upper()
        logging.getLogger(name).setLevel(level)
````

## File: src/mcp_project_context_server/helpers/sections.py
````python
"""Heading-boundary markdown splitting, shared by the indexer and (future) ADR section tools.

Implements the chunking strategy from ADR-00007: split on top-level (``##``)
headings only, preserving heading text as the first line of each resulting
chunk, with a staged fallback for sections that exceed a caller-supplied
maximum size (natural paragraph breaks, then ``###`` sub-headings, then
allowing an oversized chunk as a last resort).
"""
import re
from dataclasses import dataclass

_TOP_HEADING_RE = re.compile(r"^##(?!#)[ \t]+(.*)$", re.MULTILINE)
_SUB_HEADING_RE = re.compile(r"^###(?!#)[ \t]+.*$", re.MULTILINE)
_TITLE_RE = re.compile(r"^#(?!#)[ \t]+(.*)$", re.MULTILINE)


@dataclass
class Section:
    """One top-level (``##``) section of a markdown document.

    :ivar name: The heading text, or the document's ``#`` title (or ``""``)
        for content preceding the first ``##`` heading.
    :ivar content: The section's raw content, with its heading line (if any)
        included as the first line.
    """

    name: str
    content: str


def split_sections(text: str) -> list[Section]:
    """Split *text* into `Section`s on top-level (``##``) headings only.

    Content preceding the first ``##`` heading (e.g. an ADR's ``# Title``
    line) becomes its own leading `Section`, named from the document's ``#``
    title line if present, else ``""``. It is omitted if blank.

    :param text: (str) The full markdown document content.
    :return: (list) `Section`s in document order.
    """
    matches = list(_TOP_HEADING_RE.finditer(text))
    sections: list[Section] = []

    preamble_end = matches[0].start() if matches else len(text)
    preamble = text[:preamble_end]
    if preamble.strip():
        title_match = _TITLE_RE.search(preamble)
        preamble_name = title_match.group(1).strip() if title_match else ""
        sections.append(Section(name=preamble_name, content=preamble))

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append(Section(name=match.group(1).strip(), content=text[start:end]))

    return sections


def _pack_paragraphs(paragraphs: list[str], max_chars: int, sep: str) -> list[str]:
    """Greedily pack *paragraphs* into pieces no longer than *max_chars* where possible."""
    pieces: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in paragraphs:
        added_len = len(para) if not current else len(para) + len(sep)
        if current and current_len + added_len > max_chars:
            pieces.append(sep.join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += added_len

    if current:
        pieces.append(sep.join(current))

    return pieces


def _split_oversized(body: str, max_chars: int) -> list[str]:
    """Apply the staged natural-break -> ``###`` -> oversized-fallback split to *body*."""
    paragraphs = re.split(r"\n\s*\n", body)
    pieces = _pack_paragraphs(paragraphs, max_chars, sep="\n\n")

    result: list[str] = []
    for piece in pieces:
        if len(piece) <= max_chars:
            result.append(piece)
            continue

        sub_matches = list(_SUB_HEADING_RE.finditer(piece))
        if not sub_matches:
            result.append(piece)
            continue

        sub_pieces: list[str] = []
        first_start = sub_matches[0].start()
        if piece[:first_start].strip():
            sub_pieces.append(piece[:first_start])
        for i, match in enumerate(sub_matches):
            start = match.start()
            end = sub_matches[i + 1].start() if i + 1 < len(sub_matches) else len(piece)
            sub_pieces.append(piece[start:end])
        result.extend(sub_pieces)

    return result


def chunk_section(section: Section, max_chars: int) -> list[str]:
    """Split *section* into one or more chunk strings no longer than *max_chars*, where possible.

    A section within the limit is returned unchanged as a single chunk. An
    oversized section is split on paragraph boundaries first, falling back to
    ``###`` sub-headings for any still-oversized piece, and finally left
    oversized if no further natural break is available. Every returned chunk
    is prefixed with the section's heading line so heading text remains the
    first line of each chunk.

    :param section: (Section) The section to split.
    :param max_chars: (int) The target maximum chunk size in characters.
    :return: (list) One or more chunk strings, in document order.
    """
    if len(section.content) <= max_chars:
        return [section.content]

    heading_match = _TOP_HEADING_RE.match(section.content) or _TITLE_RE.match(section.content)
    if heading_match:
        heading_line = section.content[: heading_match.end()]
        body = section.content[heading_match.end() :].lstrip("\n")
    else:
        heading_line = f"## {section.name}" if section.name else ""
        body = section.content

    pieces = _split_oversized(body, max_chars)
    if not heading_line:
        return pieces

    return [f"{heading_line}\n\n{piece.strip()}" if piece.strip() else heading_line for piece in pieces]
````

## File: src/mcp_project_context_server/integrations/embeddings/__init__.py
````python
"""Embedding provider integrations."""
````

## File: src/mcp_project_context_server/integrations/embeddings/cohere/__init__.py
````python
"""Cohere embedding provider — implements the EmbeddingProvider Protocol."""
````

## File: src/mcp_project_context_server/integrations/embeddings/google/__init__.py
````python
"""Google Gemini API embedding provider — implements the EmbeddingProvider Protocol."""
````

## File: src/mcp_project_context_server/integrations/embeddings/ollama/__init__.py
````python
"""Ollama embedding provider package."""
````

## File: src/mcp_project_context_server/integrations/embeddings/openai/__init__.py
````python
"""OpenAI embedding provider — implements the EmbeddingProvider Protocol."""
````

## File: src/mcp_project_context_server/integrations/embeddings/vertexai/__init__.py
````python
"""Google Vertex AI embedding provider — implements the EmbeddingProvider Protocol."""
````

## File: src/mcp_project_context_server/integrations/embeddings/vertexai/client.py
````python
"""Google Vertex AI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`VERTEXAI_PROJECT`
    Google Cloud project ID.  **Required.**

`VERTEXAI_LOCATION`
    Google Cloud region, e.g. `us-central1`.  **Required.**

`VERTEXAI_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `text-embedding-004`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "text-embedding-004"
# Conservative character limit matching the model's context window
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class GoogleVertexEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Google Vertex AI SDK.

    The `vertexai` package is imported lazily inside `_get_embedding_model()`
    so that the provider can be constructed without requiring the package to
    be installed unless it is actually used. The `TextEmbeddingModel` is
    resolved on first use and cached for subsequent calls.

    The SDK is configured with `api_transport="rest"` to force plain HTTP
    instead of gRPC. gRPC's C-core polling engine (used by both its
    synchronous and `grpc.aio` async clients) can deadlock when it shares a
    process with asyncio's `ProactorEventLoop` — the loop this server
    requires on Windows for stdio subprocess support. REST has no such
    conflict, so the embedding call is made with the synchronous
    `get_embeddings()` wrapped in `asyncio.to_thread`, same as every other
    HTTP-based provider in this package.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `VERTEXAI_PROJECT` or `VERTEXAI_LOCATION` are not set.
        """
        project = os.getenv("VERTEXAI_PROJECT")
        if not project:
            raise EnvironmentError("VERTEXAI_PROJECT environment variable is not set.")
        location = os.getenv("VERTEXAI_LOCATION")
        if not location:
            raise EnvironmentError("VERTEXAI_LOCATION environment variable is not set.")
        self._project: str = project
        self._location: str = location
        self._model: str = os.getenv("VERTEXAI_EMBED_MODEL", _DEFAULT_MODEL)
        self._embedding_model = None

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "vertexai"

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use."""
        return self._model

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters."""
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    def _get_embedding_model(self):
        """Resolve and cache the `TextEmbeddingModel`, initializing the SDK on first use.

        Configures the SDK to use REST rather than gRPC — see the class
        docstring for why gRPC is unsafe in this server's event loop.
        """
        if self._embedding_model is None:
            import vertexai  # lazy import
            from vertexai.language_models import TextEmbeddingModel  # lazy import

            vertexai.init(project=self._project, location=self._location, api_transport="rest")
            self._embedding_model = TextEmbeddingModel.from_pretrained(self._model)
        return self._embedding_model

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Vertex AI embedding model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Vertex AI SDK returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            model = self._get_embedding_model()
            embeddings = await asyncio.wait_for(
                asyncio.to_thread(model.get_embeddings, [text]),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(embeddings[0].values)
        except Exception as exc:
            raise EmbeddingError(
                f"Google Vertex AI embedding failed (project={self._project}, model={self._model}): {exc}"
            ) from exc
````

## File: src/mcp_project_context_server/integrations/embeddings/voyage/__init__.py
````python
"""Voyage AI embedding provider — implements the EmbeddingProvider Protocol."""
````

## File: src/mcp_project_context_server/integrations/repository/__init__.py
````python
"""Repository provider integrations — local filesystem, GitHub, GitLab, and Gitea."""
````

## File: src/mcp_project_context_server/integrations/repository/gitea/__init__.py
````python
"""Gitea repository provider."""
````

## File: src/mcp_project_context_server/integrations/repository/github/__init__.py
````python
"""GitHub repository provider."""
````

## File: src/mcp_project_context_server/integrations/repository/gitlab/__init__.py
````python
"""GitLab repository provider."""
````

## File: src/mcp_project_context_server/integrations/repository/local/__init__.py
````python
"""Local filesystem repository provider."""
````

## File: src/mcp_project_context_server/integrations/vectorstore/__init__.py
````python
"""Vector store provider abstraction package."""
````

## File: src/mcp_project_context_server/integrations/vectorstore/chroma_http/__init__.py
````python
"""Vector store: chroma-http provider package."""
````

## File: src/mcp_project_context_server/integrations/vectorstore/chroma_local/__init__.py
````python
"""Vector store: chroma-local provider package."""
````

## File: src/mcp_project_context_server/integrations/vectorstore/gcp_vector_search/__init__.py
````python
"""GCP Vertex AI Vector Search vector store provider package."""
````

## File: src/mcp_project_context_server/integrations/vectorstore/gcp_vector_search/client.py
````python
"""GCP Vertex AI Vector Search vector store provider.

See ADR-00023 for the full design rationale. Summary:

Configuration
-------------
``GCP_VECTOR_SEARCH_PROJECT``
    Google Cloud project ID.  **Required.**

``GCP_VECTOR_SEARCH_LOCATION``
    Google Cloud region, e.g. ``us-central1``.  **Required.**

``GCP_VECTOR_SEARCH_INDEX_ID``
    Resource ID (or full resource name) of a pre-provisioned Vertex AI
    ``MatchingEngineIndex``.  **Required.**  The index must use
    ``index_update_method="STREAM_UPDATE"`` -- batch-update indexes do not
    support the real-time ``upsert_datapoints``/``remove_datapoints`` calls
    this provider relies on.

``GCP_VECTOR_SEARCH_INDEX_ENDPOINT_ID``
    Resource ID (or full resource name) of a pre-provisioned
    ``MatchingEngineIndexEndpoint``.  **Required.**

``GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID``
    The ``deployed_index_id`` under which the index above is deployed to the
    endpoint.  **Required.**

``GCP_VECTOR_SEARCH_FIRESTORE_COLLECTION``
    Firestore collection name used as the document/metadata sidecar.
    Optional, defaults to ``vector_store_documents``.

Design
------
This provider **never creates, deploys, or deletes Vertex AI infrastructure**
(ADR-00023).  It targets an Index/IndexEndpoint that must already exist;
``create_collection`` and ``upsert`` raise a clear error if they don't.

Vertex AI Vector Search has no native notion of a "collection" and its
``find_neighbors`` query only returns datapoint IDs and distances -- no
document text or metadata.  Two mechanisms fill that gap:

* **Multi-collection namespacing**: every datapoint is tagged with a
  ``restricts`` entry in the ``"collection"`` namespace equal to its
  collection name, and every query applies a matching restrict filter.  This
  lets multiple logical collections share one physical index.
* **Firestore sidecar**: document text and metadata are stored in Firestore,
  keyed by datapoint ID, and looked up after each ``find_neighbors`` call.
  A second, per-collection Firestore document (in a ``"{collection}__meta"``
  companion collection) holds the collection-level metadata dict and the set
  of known datapoint IDs, so ``create_collection``/``delete_collection`` know
  which datapoints to remove from the index without a native "list by
  restrict" API.
"""

import asyncio
import logging
import os
from typing import Any, Optional

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)

logger = logging.getLogger(__name__)

_COLLECTION_NAMESPACE = "collection"
_DEFAULT_FIRESTORE_COLLECTION = "vector_store_documents"
_REQUIRED_ENV_VARS = (
    "GCP_VECTOR_SEARCH_PROJECT",
    "GCP_VECTOR_SEARCH_LOCATION",
    "GCP_VECTOR_SEARCH_INDEX_ID",
    "GCP_VECTOR_SEARCH_INDEX_ENDPOINT_ID",
    "GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID",
)


class GcpVectorSearchProvider:
    """Vector store backed by a pre-provisioned Vertex AI Vector Search Index + IndexEndpoint.

    See the module docstring and ADR-00023 for the collection-namespacing and
    Firestore-sidecar design this provider relies on.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If any of the required
            ``GCP_VECTOR_SEARCH_*`` environment variables are not set.
        """
        values = {name: os.getenv(name) for name in _REQUIRED_ENV_VARS}
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variable(s) for VECTOR_STORE_PROVIDER=gcp-vector-search: "
                f"{', '.join(missing)}. This provider targets a pre-provisioned Vertex AI Index and "
                "IndexEndpoint (ADR-00023) -- it does not create or deploy GCP infrastructure. Provision "
                "the Index/IndexEndpoint yourself (Terraform, gcloud, or Console), then set these "
                "variables to the resulting resource IDs."
            )

        self._project: str = values["GCP_VECTOR_SEARCH_PROJECT"]  # type: ignore[assignment]
        self._location: str = values["GCP_VECTOR_SEARCH_LOCATION"]  # type: ignore[assignment]
        self._index_id: str = values["GCP_VECTOR_SEARCH_INDEX_ID"]  # type: ignore[assignment]
        self._index_endpoint_id: str = values["GCP_VECTOR_SEARCH_INDEX_ENDPOINT_ID"]  # type: ignore[assignment]
        self._deployed_index_id: str = values["GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID"]  # type: ignore[assignment]
        self._firestore_collection: str = os.getenv(
            "GCP_VECTOR_SEARCH_FIRESTORE_COLLECTION", _DEFAULT_FIRESTORE_COLLECTION
        )

        self._index: Optional[Any] = None
        self._endpoint: Optional[Any] = None
        self._firestore: Optional[Any] = None

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "gcp-vector-search"

    @property
    def _meta_collection(self) -> str:
        """Firestore collection name holding per-collection metadata and known datapoint IDs."""
        return f"{self._firestore_collection}__meta"

    # ------------------------------------------------------------------
    # Lazy client construction
    # ------------------------------------------------------------------

    def _get_index(self) -> Any:
        """Return the ``MatchingEngineIndex`` handle, initialising the SDK on first use."""
        if self._index is None:
            from google.cloud import aiplatform  # lazy import

            aiplatform.init(project=self._project, location=self._location)
            self._index = aiplatform.MatchingEngineIndex(index_name=self._index_id)
        return self._index

    def _get_endpoint(self) -> Any:
        """Return the ``MatchingEngineIndexEndpoint`` handle, initialising the SDK on first use."""
        if self._endpoint is None:
            from google.cloud import aiplatform  # lazy import

            aiplatform.init(project=self._project, location=self._location)
            self._endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=self._index_endpoint_id)
        return self._endpoint

    def _get_firestore(self) -> Any:
        """Return the Firestore client, initialising it on first use."""
        if self._firestore is None:
            from google.cloud import firestore  # lazy import

            self._firestore = firestore.Client(project=self._project)
        return self._firestore

    # ------------------------------------------------------------------
    # VectorStoreProvider Protocol implementation
    # ------------------------------------------------------------------

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Clear and re-register *name* for a clean re-index (ADR-00006).

        Removes every datapoint currently tagged with this collection from
        the Vertex AI index and clears its Firestore sidecar documents. Does
        **not** create, deploy, or otherwise modify the underlying Vertex AI
        Index or IndexEndpoint resources -- see ADR-00023.

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        :raises VectorStoreError: If the Vertex AI or Firestore API calls fail.
        """
        try:
            await self._remove_all_datapoints(name)

            def _write_meta() -> None:
                db = self._get_firestore()
                db.collection(self._meta_collection).document(name).set(
                    {"metadata": metadata or {}, "datapoint_ids": []}
                )

            await asyncio.to_thread(_write_meta)
        except Exception as exc:
            raise VectorStoreError(f"Failed to create/clear collection '{name}': {exc}") from exc

    async def delete_collection(self, name: str) -> None:
        """Remove all datapoints and sidecar data for *name*.  Silently succeeds if it does not exist.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        try:
            await self._remove_all_datapoints(name)

            def _delete_meta() -> None:
                db = self._get_firestore()
                db.collection(self._meta_collection).document(name).delete()

            await asyncio.to_thread(_delete_meta)
        except Exception:
            pass

    async def _remove_all_datapoints(self, name: str) -> None:
        """Remove every datapoint and document tagged with collection *name*."""
        datapoint_ids = await self._get_known_datapoint_ids(name)
        if not datapoint_ids:
            return

        def _sync() -> None:
            index = self._get_index()
            index.remove_datapoints(datapoint_ids=datapoint_ids)
            db = self._get_firestore()
            for doc_id in datapoint_ids:
                db.collection(self._firestore_collection).document(doc_id).delete()

        await asyncio.to_thread(_sync)

    async def _get_known_datapoint_ids(self, name: str) -> list[str]:
        """Return the datapoint IDs previously recorded for collection *name*."""

        def _sync() -> list[str]:
            db = self._get_firestore()
            doc = db.collection(self._meta_collection).document(name).get()
            if not doc.exists:
                return []
            return list(doc.to_dict().get("datapoint_ids") or [])

        return await asyncio.to_thread(_sync)

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Insert or update documents in *collection_name*.

        :param collection_name: (str) Target collection.
        :param ids: (list) Per-document unique identifiers.
        :param embeddings: (list) Per-document embedding vectors (must all be the same length).
        :param documents: (list) Raw text for each document.
        :param metadatas: (list) Per-document metadata dicts.
        :return: (None) This method does not return a value.
        :raises VectorStoreError: If the Vertex AI or Firestore API calls fail.
        """
        if not ids:
            return

        def _sync() -> None:
            index = self._get_index()
            datapoints = [
                {
                    "datapoint_id": doc_id,
                    "feature_vector": embedding,
                    "restricts": [{"namespace": _COLLECTION_NAMESPACE, "allow": [collection_name]}],
                }
                for doc_id, embedding in zip(ids, embeddings)
            ]
            index.upsert_datapoints(datapoints=datapoints)

            db = self._get_firestore()
            batch = db.batch()
            for doc_id, document, meta in zip(ids, documents, metadatas):
                ref = db.collection(self._firestore_collection).document(doc_id)
                batch.set(ref, {"collection": collection_name, "document": document, "metadata": meta})
            batch.commit()

            meta_ref = db.collection(self._meta_collection).document(collection_name)
            meta_doc = meta_ref.get()
            existing_ids = set(meta_doc.to_dict().get("datapoint_ids") or []) if meta_doc.exists else set()
            meta_ref.set(
                {
                    "metadata": meta_doc.to_dict().get("metadata", {}) if meta_doc.exists else {},
                    "datapoint_ids": sorted(existing_ids | set(ids)),
                }
            )

        try:
            await asyncio.to_thread(_sync)
        except Exception as exc:
            raise VectorStoreError(f"Upsert failed on collection '{collection_name}': {exc}") from exc

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run a ``find_neighbors`` nearest-neighbour search scoped to *collection_name*.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the collection does not exist or the query fails.
        """

        def _sync() -> QueryResult:
            from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import Namespace  # lazy import

            endpoint = self._get_endpoint()
            response = endpoint.find_neighbors(
                deployed_index_id=self._deployed_index_id,
                queries=[query_embedding],
                num_neighbors=n_results,
                filter=[Namespace(name=_COLLECTION_NAMESPACE, allow_tokens=[collection_name])],
            )
            neighbors = response[0] if response else []
            ids = [n.id for n in neighbors]
            distances = [float(n.distance) for n in neighbors]

            db = self._get_firestore()
            documents: list[str] = []
            metadatas: list[dict] = []
            for doc_id in ids:
                snap = db.collection(self._firestore_collection).document(doc_id).get()
                data = snap.to_dict() if snap.exists else {}
                documents.append(data.get("document", ""))
                metadatas.append(data.get("metadata", {}))

            return QueryResult(ids=ids, documents=documents, metadatas=metadatas, distances=distances)

        try:
            return await asyncio.to_thread(_sync)
        except Exception as exc:
            raise VectorStoreError(f"Query failed on collection '{collection_name}': {exc}") from exc

    async def count(self, collection_name: str) -> int:
        """Return the number of datapoints known for *collection_name* (0 if absent).

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        try:
            return len(await self._get_known_datapoint_ids(collection_name))
        except Exception:
            return 0

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if a sidecar metadata document exists for *collection_name*.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """

        def _sync() -> bool:
            db = self._get_firestore()
            return db.collection(self._meta_collection).document(collection_name).get().exists

        try:
            return await asyncio.to_thread(_sync)
        except Exception:
            return False

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return the metadata dict stored for *collection_name* (``{}`` if absent).

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection does not exist.
        """

        def _sync() -> dict:
            db = self._get_firestore()
            doc = db.collection(self._meta_collection).document(collection_name).get()
            if not doc.exists:
                return {}
            return doc.to_dict().get("metadata") or {}

        try:
            return await asyncio.to_thread(_sync)
        except Exception:
            return {}

    def reset_for_testing(self) -> None:
        """Reset cached SDK handles.  **For use in tests only.**

        :return: (None) This method does not return a value.
        """
        self._index = None
        self._endpoint = None
        self._firestore = None
````

## File: src/mcp_project_context_server/integrations/vectorstore/pgvector/__init__.py
````python
"""Vector store: pgvector provider package."""
````

## File: src/mcp_project_context_server/tools/find_latest_session_file.py
````python
"""Tool: find_latest_session_file — deterministic lookup of the newest session file."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.context_files import list_context_files
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``find_latest_session_file`` tool call.

    :param arguments: (dict) Tool input dict. Requires key ``"project_path"``.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        naming the most recent ``sessions/*.md`` file (sorted by filename), or
        "No session files found." when none exist.
    """
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    session_files = await list_context_files(_project_path, prefix="sessions/")
    if not session_files:
        return [types.TextContent(type="text", text="No session files found.")]

    return [types.TextContent(type="text", text=f"Latest session file: {session_files[-1]}")]
````

## File: src/mcp_project_context_server/tools/load_context_files.py
````python
"""Tool: load_context_files — load specific .context/ files, tagged with path + SHA-512."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.context_files import format_tagged_file, hash_content, resolve_requested_files
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``load_context_files`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"`` and
        ``"files"`` (a list of ``.context/``-relative paths to load).
    :return: (list) One :class:`~mcp.types.TextContent` block per requested file —
        a ``<context-file path="..." sha512="...">`` tagged block for files that
        were found, or a "File not found" message for files that were not.
    """
    files: list[str] = arguments["files"]
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    found, _missing = await resolve_requested_files(_project_path, files)

    blocks: list[types.TextContent] = []
    for path in files:
        if path in found:
            content = found[path]
            blocks.append(types.TextContent(type="text", text=format_tagged_file(path, hash_content(content), content)))
        else:
            blocks.append(types.TextContent(type="text", text=f"File not found: {path}"))

    return blocks
````

## File: src/mcp_project_context_server/tools/reload_active_context_file.py
````python
"""Tool: reload_active_context_file — refresh files whose on-disk content changed."""
import logging
import os

from mcp import types

from mcp_project_context_server.helpers.context_files import format_tagged_file, hash_content, resolve_requested_files
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``reload_active_context_file`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"`` and
        ``"files"`` — a list of ``{"path": ..., "known_sha512": ...}`` entries
        describing files currently held in active context.
    :return: (list) One :class:`~mcp.types.TextContent` block per entry: "No change"
        when the current SHA-512 matches ``known_sha512``, a fresh tagged block
        plus a discard note when it differs, or "File not found" when the file
        no longer exists.
    """
    entries: list[dict] = arguments["files"]
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    paths = [entry["path"] for entry in entries]
    found, _missing = await resolve_requested_files(_project_path, paths)

    blocks: list[types.TextContent] = []
    for entry in entries:
        path = entry["path"]
        known_sha512 = entry["known_sha512"]

        if path not in found:
            blocks.append(types.TextContent(type="text", text=f"File not found: {path}"))
            continue

        content = found[path]
        current_sha512 = hash_content(content)
        if current_sha512 == known_sha512:
            blocks.append(types.TextContent(type="text", text=f"No change: {path}"))
            continue

        tagged = format_tagged_file(path, current_sha512, content)
        blocks.append(
            types.TextContent(
                type="text",
                text=f"{tagged}\n\nNote: '{path}' changed — discard the stale block previously loaded for this path.",
            )
        )

    return blocks
````

## File: src/mcp_project_context_server/tools/search_adr_index.py
````python
"""Tool: search_adr_index — semantic search scoped to .context/decisions/."""
import logging
import os

from mcp import types

from mcp_project_context_server.tools.search_shared import run_search

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``search_adr_index`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"query"``; optional key ``"n_results"`` (defaults to 5).
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        with matching ``decisions/`` snippets, or an error/"not found" message.
    """
    query: str = arguments["query"]
    n_results: int = arguments.get("n_results", 5)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    return await run_search(_project_path, query, n_results, file_prefix="decisions/")
````

## File: src/mcp_project_context_server/tools/search_context_index.py
````python
"""Tool: search_context_index — semantic search over the whole indexed context."""
import logging
import os

from mcp import types

from mcp_project_context_server.tools.search_shared import run_search

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``search_context_index`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"query"``; optional key ``"n_results"`` (defaults to 5).
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        with the matching context snippets, or an error/"not found" message.
    """
    query: str = arguments["query"]
    n_results: int = arguments.get("n_results", 5)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    return await run_search(_project_path, query, n_results, file_prefix=None)
````

## File: src/mcp_project_context_server/tools/search_session_files.py
````python
"""Tool: search_session_files — semantic search scoped to .context/sessions/."""
import logging
import os

from mcp import types

from mcp_project_context_server.tools.search_shared import run_search

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``search_session_files`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"query"``; optional key ``"n_results"`` (defaults to 5).
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        with matching ``sessions/`` snippets, or an error/"not found" message.
    """
    query: str = arguments["query"]
    n_results: int = arguments.get("n_results", 5)
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    return await run_search(_project_path, query, n_results, file_prefix="sessions/")
````

## File: src/mcp_project_context_server/transport/__init__.py
````python
"""Transport layer package — STDIO and HTTP/SSE transports."""
````

## File: CONTRIBUTING.md
````markdown
# Contributing to MCP Project Context Server

Thank you for your interest in contributing to **MCP Project Context Server**! This document outlines the standards and processes that all contributors are expected to follow. Taking the time to read it before submitting changes will make the review process faster and smoother for everyone.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Branching Strategy](#branching-strategy)
- [Making Changes](#making-changes)
- [Commit Message Standards](#commit-message-standards)
- [Unit Testing Requirements](#unit-testing-requirements)
- [Linting and Code Style](#linting-and-code-style)
- [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs)
- [Pull Request Guidelines](#pull-request-guidelines)
- [PR Template](#pr-template)
- [Review Process](#review-process)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

All contributors are expected to behave professionally and respectfully. Harassment, discrimination, or abusive behavior of any kind will not be tolerated. By participating in this project you agree to uphold these expectations in all interactions — issues, pull requests, code reviews, and discussions alike.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/mcp-project-context-server.git
   cd mcp-project-context-server
   ```
3. **Add the upstream remote** so you can stay in sync:
   ```bash
   git remote add upstream https://github.com/DarkMatterProductions/mcp-project-context-server.git
   ```

---

## Development Environment Setup

### Prerequisites

- **Python 3.11+**
- **Ollama** running locally with an embedding model (e.g., `nomic-embed-text`)
- **ChromaDB** (installed automatically as a dependency)

### Install with Development Dependencies

```bash
pip install -e .
pip install testsuite
```

### Verify Your Setup

```bash
# Run the test suite
pytest tests/

# Check linting
flake8 src/
black --check src/
isort --check-only src/
mypy src/
```

---

## Branching Strategy

- **`main`** — stable, releasable code only. Direct pushes are not permitted.
- **Feature branches** — branch off `main` using a descriptive name:
  - `feature/<short-description>` — new functionality
  - `fix/<short-description>` — bug fixes
  - `docs/<short-description>` — documentation-only changes
  - `adr/<ADR-XXXXX-topic>` — ADR additions or updates
  - `chore/<short-description>` — maintenance tasks (dependency updates, CI, etc.)

Always keep your branch up to date with `main` before opening a PR:

```bash
git fetch upstream
git rebase upstream/main
```

---

## Making Changes

Before writing any code, consider whether your change:

- Affects more than one component or module
- Introduces a new integration or dependency
- Reverses or contradicts an existing architectural decision
- Has non-obvious trade-offs or could be misunderstood later

If any of these apply, an ADR may be required. See [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs).

---

## Commit Message Standards

Every commit must include a **clear, detailed message** that explains both *what* changed and *why*. Vague messages like `"fix bug"` or `"update code"` will not be accepted.

### Format

```
<type>(<scope>): <short summary — imperative mood, max 72 chars>

<body — itemized list explaining the motivation, context, and any relevant detail>

<footer — optional: issue references, ADR references, breaking change notices>
```

### Best Practices

#### Subject Line (First Line)
- Use the **`<type>(<scope>):`** prefix from the types table below
- Write in **imperative mood** — *"add feature"* not *"added feature"*
- Keep it **≤ 72 characters**
- Be specific — avoid vague summaries like `"fix bug"` or `"update code"`

#### Body
- Separate from the subject line with a **blank line**
- Use an **itemized list** to explain:
  - **What** changed
  - **Why** it changed (motivation)
  - Any relevant **context or trade-offs**
- Do not simply restate the subject — explain the *reasoning*

#### Footer
- Reference closed issues: `Closes #42`
- Reference relevant ADRs: `ADR-00001`
- Note breaking changes if applicable

### Types

| Type        | When to use                                         |
|-------------|-----------------------------------------------------|
| `breaking`  | A backwards incompatible change to the API or Tools |
| `rewrite`   | Complete rewrites / architectural overhauls         |
| `milestone` | Significant feature milestones / stable releases    |
| `deprecate` | Major deprecation cleanups                          |
| `eos`       | End of support for a runtime/platform               |
| `license`   | License changes                                     |
| `security`  | Security-mandated incompatible changes              |
| `feat`      | A new feature or capability                         |
| `fix`       | A bug fix                                           |
| `test`      | Adding or updating tests                            |
| `docs`      | Documentation changes only                          |
| `refactor`  | Code restructuring with no behaviour change         |
| `chore`     | Build system, tooling, or dependency changes        |
| `adr`       | Adding or updating an Architecture Decision Record  |

### No-Release Scopes

Certain scopes suppress version bumping **regardless of the commit type**. Even a `fix` or `feature` commit will not trigger a release if its scope is one of the following:

| Scope     | When to use                                                         |
|-----------|---------------------------------------------------------------------|
| `ci`      | Changes to CI/CD pipeline configuration or workflow files           |
| `tools`   | Changes to scripts or utilities under `.github/tools/`              |

These scopes are enforced by `build_and_publish.py` via the `NO_RELEASE_SCOPES` constant. When a commit matches a no-release scope, `determine_bump()` sets `has_none = True` and skips all further bump checks for that commit — meaning even a `fix(ci):` or `feature(tools):` commit will produce `bump=none` in `GITHUB_OUTPUT` and skip the PyPI publish step.

If a new no-release scope is needed, add it to the `NO_RELEASE_SCOPES` set in `build_and_publish.py` **and** document it in this table.

**Example:**
```
fix(ci): correct PyPI publish condition in build-and-publish.yml

- The publish step was not correctly gating on the bump output variable
- Updated the if-condition to reference the correct step id
```

### Examples

```
feat(search): add n_results parameter to search_project_context

- The tool previously returned a hardcoded limit of 5 results with no
  way for callers to control the result count
- Exposes n_results as a configurable parameter so callers can tune
  result volume to their use case
- Defaults to 5 to preserve full backward compatibility

Closes #42
Related ADR(s): ADR-XXXXXX
```

```
fix(indexer): handle empty .context/decisions directory gracefully

- The indexer raised a FileNotFoundError when the decisions directory
  existed but contained no .md files
- Added an early return with an informational log message to handle
  this edge case cleanly
- No behaviour change for non-empty directories

Closes #57
```

---

## Unit Testing Requirements

All code changes **must** be accompanied by unit tests. Pull requests that modify logic without corresponding test coverage will not be merged.

### Standards

- **Tests for application source code** live in the `tests/` directory and follow the naming convention `test_<module_name>.py`.
- **Tests for scripts under `.github/tools/`** live **alongside the script** in `.github/tools/`, following the same `test_<script_name>.py` naming convention. Each tools subdirectory maintains its own `conftest.py` for path configuration. Do **not** place tooling script tests in `tests/`.
- **Async functions** must use `pytest-asyncio` and be decorated with `@pytest.mark.asyncio` (or rely on `asyncio_mode = "auto"` in `pyproject.toml`).
- **External dependencies** (ChromaDB, Ollama, filesystem I/O) **must be mocked** in unit tests using `pytest-mock`. Unit tests should never require a running external service.
- **New tools or helper functions** require tests for:
  - The happy path
  - Relevant error/edge cases (empty input, missing files, service unavailability, etc.)

### Coverage Requirement

The project targets **≥ 100% line and branch coverage**. Ensure your changes do not reduce coverage below this threshold. Check coverage locally before submitting:

```bash
pytest --cov=src/mcp_project_context_server --cov-report=term-missing tests/
```

### Running the Full Test Suite

```bash
# Application source tests
pytest tests/

# CI/tooling script tests
pytest .github/tools/

# All tests
pytest tests/ .github/tools/

# With coverage report (application source)
pytest --cov=src/mcp_project_context_server tests/

# A specific test file
pytest tests/test_tool_search_context.py -v
pytest .github/tools/test_build_and_publish.py -v
```

---

## Linting and Code Style

All code must conform to the linting and formatting rules configured in `pyproject.toml`. CI will enforce these checks — fix all issues locally before pushing.

### Tools in Use

| Tool     | Purpose                    | Configuration                       |
|----------|----------------------------|-------------------------------------|
| `flake8` | Style and error checking   | `[tool.flake8]` in `pyproject.toml` |
| `black`  | Opinionated code formatter | `[tool.black]` in `pyproject.toml`  |
| `isort`  | Import ordering            | `[tool.isort]` in `pyproject.toml`  |
| `mypy`   | Static type checking       | `[tool.mypy]` in `pyproject.toml`   |

### Key Rules

- **Line length:** `black` is configured to `240` characters; `flake8` enforces `120` characters for non-formatted sections. Do not introduce lines that violate the `flake8` maximum.
- **Import ordering:** `isort` is configured with `profile = "black"`. Run `isort src/` before committing.
- **Type annotations:** All new public functions and methods must include type annotations. `mypy` is run in CI with `ignore_missing_imports = true`.
- **Docstrings:** Public modules, classes, and functions should have docstrings. Note that several docstring warnings (D100, D104, D105, etc.) are suppressed — see `[tool.flake8]` for the full ignore list.

### Running the Linters

```bash
# Check formatting (non-destructive)
black --check src/
isort --check-only src/
flake8 src/
mypy src/

# Auto-fix formatting
black src/
isort src/
```

All four checks must pass with zero errors before a PR will be reviewed.

---

## Architecture Decision Records (ADRs)

This project uses **Architecture Decision Records** to document significant design decisions. All contributors must understand and honor the ADRs stored in `.context/decisions/`. The full process is described in [`.context/adr-creation-and-review-process.md`](.context/adr-creation-and-review-process.md).

### When an ADR Is Required

Create a new ADR before — not after — implementing any change that:

- Affects more than one component or service
- Introduces or replaces a dependency, integration, or storage backend
- Changes a behavior that was the subject of a previous ADR
- Has non-obvious trade-offs or could be costly to reverse
- Reflects a constraint, policy, or organizational requirement

If you are uncertain whether your change warrants an ADR, open an issue and ask. When in doubt, write the ADR.

### Honoring Existing ADRs

Before writing code, review the relevant ADRs in `.context/decisions/`. Contributions must not:

- Contradict or circumvent an `Accepted` or `Implemented` ADR without first superseding it through the formal ADR process.
- Re-litigate a settled decision in a PR without opening a new ADR.

If you believe an existing decision should be revisited, create a new `Proposed` ADR referencing the original, and initiate the review process described in `.context/adr-creation-and-review-process.md`.

### ADR File Conventions

- **Location:** `.context/decisions/`
- **Naming:** `ADR-XXXXX-<kebab-case-topic>.md` (zero-padded 5-digit number)
- **Template:** Use the exact template defined in `.context/adr-creation-and-review-process.md`. Do not add or remove sections.
- **Never delete** an ADR file, even if it is deprecated or superseded.

### Commit Convention for ADRs

```
adr(ADR-XXXXX): accept decision on <topic>
```

---

## Pull Request Guidelines

### Before Opening a PR

Ensure the following are true:

- [ ] All tests pass locally: `pytest tests/`
- [ ] Coverage has not dropped below 100%: `pytest --cov=src/mcp_project_context_server tests/`
- [ ] All linters pass with zero errors: `black --check src/ && isort --check-only src/ && flake8 src/ && mypy src/`
- [ ] Any new or changed public APIs have type annotations and docstrings
- [ ] Any architectural change is covered by a new or updated ADR
- [ ] Your branch is up to date with `main`

### PR Title

Write the title in **imperative mood** as a plain summary of the change — ≤ 72 characters. Do **not** use a `<type>(<scope>):` prefix in the title. Type and scope information belongs in the **Change Types** table in the PR description (see below), because a single PR may span multiple commit types and a single-type prefix would lose that signal.

**Good:** `Add semantic versioning and release automation script`
**Bad:** `chore(ci): add semantic versioning and release automation script`

### PR Description

Every PR **must** include a thorough description using the template at `.github/PULL_REQUEST_TEMPLATE.md`. The following sections are required:

#### Change Types
A table mapping each `type` and `scope` present in the PR's commits to a short description of what that group of changes covers. This replaces the single-type prefix that would appear in a commit subject line.

```markdown
## Change Types

| Type | Scope |
|------|-------|
| `chore` | `ci` |
| `docs` | `claude` |
```

Every distinct `type(scope)` combination in the PR's commits must appear as a row. Use the type values defined in the [Commit Message Standards](#commit-message-standards) types table.

#### Summary
A clear explanation of what this PR does and why. Do not simply restate the title. Explain the motivation and the problem being solved.

#### Changes Made
A concise bullet-point list of the significant changes introduced. Include files or modules affected where helpful.

#### Testing
Describe what was tested and how. Include:
- Which test files were added or modified
- Any edge cases or error conditions covered
- How to reproduce the behavior manually if relevant

#### ADRs Referenced
List any ADRs that informed, constrain, or are affected by this change. If a new ADR was created, link to it here.

#### Checklist
Include the pre-PR checklist above in your description and check off each item.

### PR Template

A GitHub PR template is provided at `.github/PULL_REQUEST_TEMPLATE.md`. It pre-populates the required sections when you open a new PR. Fill in every section — do not delete any headings.

---

## Review Process

1. **Automated checks** (linting, tests, coverage) run on every PR via CI. All checks must pass before a human review is requested.
2. **A maintainer** will review the code for correctness, test coverage, adherence to linting rules, and compliance with ADRs.
3. **Feedback** will be given via inline comments or a review summary. Address all comments before re-requesting review.
4. **Approval and merge** — once approved, a maintainer will merge the PR using squash-merge to keep the `main` history clean.

---

## Reporting Issues

If you have found a bug or have a feature request:

1. **Search existing issues** first — it may already be reported.
2. **Open a new issue** using the appropriate template (bug report or feature request).
3. Include as much context as possible: Python version, OS, environment variables (redacted), steps to reproduce, and expected vs. actual behavior.

For security vulnerabilities, **do not open a public issue**. Contact the maintainers directly at [pypi@darkmatter-productions.com](mailto:pypi@darkmatter-productions.com).

---

## Questions?

If you have questions about the contribution process or the project architecture, open a [GitHub Discussion](https://github.com/DarkMatterProductions/mcp-project-context-server/discussions) or reach out via the Issues tracker.

---

<div align="center">

**Thank you for contributing to MCP Project Context Server.**

</div>
````

## File: requirements.txt
````
mcp
chromadb
ollama>=0.4.0
watchdog
pyyaml
````

## File: src/mcp_project_context_server/helpers/__init__.py
````python
"""Shared helper utilities package."""
````

## File: src/mcp_project_context_server/indexing/__init__.py
````python
"""Context indexing package."""
````

## File: src/mcp_project_context_server/indexing/indexer.py
````python
"""Shared indexing pipeline — provider-agnostic core.

Accepts any ``VectorStoreProvider`` instance.  Vector-store-specific indexers
in ``integrations/vectorstore/{provider}/indexer.py`` are responsible for
instantiating their own provider and passing it here.

No vector-store or embedding provider is imported directly.  All external
dependencies are injected via the ``store`` parameter and the embedding
registry.
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

from mcp_project_context_server.helpers.context import (
    collection_name_for,
    collection_name_for_repo_id,
    find_context_dir,
    read_context_files,
    resolve_project_path,
)
from mcp_project_context_server.helpers.context_files import hash_content
from mcp_project_context_server.helpers.sections import chunk_section, split_sections
from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider
from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider

logger = logging.getLogger(__name__)

_EMBED_CONCURRENCY: int = int(os.getenv("EMBED_CONCURRENCY", "4"))
_MAX_CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1500"))


async def run_index_pipeline(project_path: str | Path, store: VectorStoreProvider) -> str:
    """Chunk, embed concurrently, and batch-store all .context/ markdown files.

    Stamps the collection with provenance metadata (embed provider/model,
    vector store provider, repo provider, server version, indexed_at timestamp)
    so that search can detect and warn on provider/model mismatches.

    :param project_path: (str) Path to the project root or any file within it.
    :param store: (VectorStoreProvider) Fully initialized vector store provider to write into.
    :return: (str) A human-readable summary string describing what was indexed.
    """
    repo_provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(str(project_path), repo_provider.provider_name)

    if is_remote:
        try:
            files = await repo_provider.fetch_context_files(resolved_path)
        except RepositoryError as exc:
            return f"Error accessing repository {resolved_path}: {exc}"
        if not files:
            return f"No .context/ directory found in {resolved_path}"
        col_name = collection_name_for_repo_id(resolved_path)
    else:
        context_dir = find_context_dir(project_path)
        if not context_dir:
            return f"No .context/ directory found at or above {project_path}"
        col_name = collection_name_for(context_dir)
        files = read_context_files(context_dir)

    # Deferred until after the context-existence check above so that a
    # missing .context/ directory is reported even when no embedding
    # provider is configured (EMBED_PROVIDER unset).
    embed_provider = get_embedding_provider()
    max_chars = min(_MAX_CHUNK_SIZE, embed_provider.max_chars)
    embed_chunk = embed_provider.embed_chunk

    collection_metadata = {
        "embed_provider": embed_provider.provider_name,
        "embed_model": embed_provider.model_name,
        "vector_store_provider": store.provider_name,
        "repo_provider": repo_provider.provider_name,
        "server_version": __version__,
        "indexed_at": datetime.now(timezone.utc).isoformat(),
    }

    await store.create_collection(col_name, metadata=collection_metadata)

    all_chunks: list[tuple[str, str, str, int, str, str]] = []
    for filename, file_content in files.items():
        chunk_idx = 0
        for section in split_sections(file_content):
            section_sha512 = hash_content(section.content)
            for piece in chunk_section(section, max_chars):
                if piece.strip():
                    all_chunks.append((f"{filename}::{chunk_idx}", piece, filename, chunk_idx, section.name, section_sha512))
                    chunk_idx += 1

    if not all_chunks:
        return f"Indexed 0 chunks from {len(files)} files into collection '{col_name}'"

    semaphore = asyncio.Semaphore(_EMBED_CONCURRENCY)

    async def _embed(doc_id: str, chunk: str, filename: str, chunk_idx: int, section: str, section_sha512: str):
        async with semaphore:
            try:
                embedding = await embed_chunk(chunk)
                return (doc_id, chunk, embedding, filename, chunk_idx, section, section_sha512)
            except Exception as e:
                logger.warning("Failed to embed %s: %s", doc_id, e)
                return e

    results = await asyncio.gather(*[_embed(*c) for c in all_chunks])

    valid = [r for r in results if not isinstance(r, Exception)]
    if valid:
        await store.upsert(
            collection_name=col_name,
            ids=[r[0] for r in valid],
            embeddings=[r[2] for r in valid],
            documents=[r[1] for r in valid],
            metadatas=[{"file": r[3], "chunk": r[4], "section": r[5], "section_sha512": r[6]} for r in valid],
        )

    failed_count = len(all_chunks) - len(valid)
    if failed_count == len(all_chunks):
        first_error = next(r for r in results if isinstance(r, Exception))
        return (
            f"Error: failed to embed all {len(all_chunks)} chunks from {len(files)} files "
            f"— 0 chunks indexed. First error: {first_error}"
        )
    if failed_count:
        return (
            f"Indexed {len(valid)} chunks from {len(files)} files into collection '{col_name}' "
            f"({failed_count} chunks failed to embed — see server logs)"
        )

    return f"Indexed {len(valid)} chunks from {len(files)} files into collection '{col_name}'"
````

## File: src/mcp_project_context_server/integrations/__init__.py
````python
"""Third-party service integrations package."""
````

## File: src/mcp_project_context_server/integrations/embeddings/base.py
````python
"""EmbeddingProvider Protocol — the provider abstraction boundary for embeddings.

All embedding providers must implement this Protocol so that the rest of the
codebase can depend on the abstraction rather than any concrete provider.

Usage
-----
Import the protocol for type annotations::

    from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

Obtain a concrete instance from the registry::

    from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
    provider = get_embedding_provider()
"""
import logging
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol that all embedding provider implementations must satisfy.

    Implementors should be importable without triggering any network calls,
    file I/O, or expensive initialization — those should be deferred to the
    first call to ``embed_chunk()``.
    """
    @property
    def provider_name(self) -> str:
        """Short identifier for the provider, e.g. ``"ollama"``, ``"voyage"``."""
        ...

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use, e.g. ``"nomic-embed-text"``."""
        ...

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters for this model.

        Used by the chunking layer to stay within the provider's context window.
        This is an advisory value — providers may silently truncate longer inputs.
        """
        ...

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed a single text string and return the embedding vector.

        :param text: (str) The text to embed. May be up to ``max_chars`` in length.
        :return: (list) A list of floats representing the embedding vector.
        :raises EmbeddingError: If the provider returns an error or is unreachable.
        """
        ...
````

## File: src/mcp_project_context_server/integrations/embeddings/cohere/client.py
````python
"""Cohere embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`COHERE_API_KEY`
    API key for the Cohere service.  **Required.**

`COHERE_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `embed-english-v3.0`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "embed-english-v3.0"
# embed-english-v3.0: 512 token context; conservative character limit
_MAX_CHARS: int = 20_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class CohereEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Cohere Embed API.

    The `cohere` package is imported lazily inside `embed_chunk()` so that the
    provider can be imported without requiring the package to be installed.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `COHERE_API_KEY` is not set.
        """
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise EnvironmentError("COHERE_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("COHERE_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "cohere"

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use."""
        return self._model

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters."""
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Cohere embedding model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Cohere API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            import cohere  # lazy import

            client = cohere.AsyncClientV2(api_key=self._api_key)
            response = await asyncio.wait_for(
                client.embed(
                    texts=[text],
                    model=self._model,
                    input_type="search_document",
                    embedding_types=["float"],
                ),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(response.embeddings.float_[0])
        except Exception as exc:
            raise EmbeddingError(f"Cohere embedding failed (model={self._model}): {exc}") from exc
````

## File: src/mcp_project_context_server/integrations/embeddings/google/client.py
````python
"""Google Gemini API embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`GOOGLE_API_KEY`
    API key for the Google Generative AI service.  **Required.**

`GOOGLE_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `gemini-embedding-2`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "gemini-embedding-2"
# gemini-embedding-2: 2048 token context; conservative character limit
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class GoogleEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Google Generative AI (Gemini) API.

    The `google.generativeai` package is imported lazily inside `embed_chunk()` so
    that the provider can be imported without requiring the package to be installed.
    Because the `genai.embed_content` function is synchronous, it is wrapped with
    `asyncio.to_thread` to avoid blocking the event loop.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `GOOGLE_API_KEY` is not set.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("GOOGLE_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "google"

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use."""
        return self._model

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters."""
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Google Generative AI embedding model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Google API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            import google.generativeai as genai  # lazy import

            genai.configure(api_key=self._api_key)
            result = await asyncio.wait_for(
                asyncio.to_thread(genai.embed_content, model=self._model, content=text),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(result["embedding"])
        except Exception as exc:
            raise EmbeddingError(f"Google embedding failed (model={self._model}): {exc}") from exc
````

## File: src/mcp_project_context_server/integrations/embeddings/ollama/client.py
````python
"""Ollama embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`OLLAMA_HOST`
    Base URL for the Ollama server.  Defaults to `http://localhost:11434`.

`OLLAMA_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `nomic-embed-text`.

`EMBED_CONCURRENCY`
    Maximum number of concurrent embedding requests.  Defaults to `4`.
    (Respected by the caller — not enforced here.)
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_HOST: str = "http://localhost:11434"
_DEFAULT_MODEL: str = "nomic-embed-text"
# Conservative character limit for nomic-embed-text (8192 token context ≈ 32 000 chars)
_MAX_CHARS: int = 32_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by a locally running Ollama server.

    This class is intentionally stateless with respect to the Ollama client —
    a fresh `AsyncClient` is obtained per call so that there are no
    long-lived connection objects to manage.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables."""
        self._host: str = os.getenv("OLLAMA_HOST", _DEFAULT_HOST)
        self._model: str = os.getenv("OLLAMA_EMBED_MODEL", os.getenv("EMBED_MODEL", _DEFAULT_MODEL))

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def max_chars(self) -> int:
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Ollama model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Ollama server returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            import ollama
            client = ollama.Client(host=self._host)
            response = await asyncio.wait_for(
                asyncio.to_thread(client.embed, model=self._model, input=text),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(response.embeddings[0])
        except Exception as exc:
            raise EmbeddingError(f"Ollama embedding failed (host={self._host}, model={self._model}): {exc}") from exc
````

## File: src/mcp_project_context_server/integrations/embeddings/openai/client.py
````python
"""OpenAI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`OPENAI_API_KEY`
    API key for the OpenAI service.  **Required.**

`OPENAI_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `text-embedding-3-small`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "text-embedding-3-small"
# text-embedding-3-small: 8191 token context; conservative character limit
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the OpenAI Embeddings API.

    The `openai` package is imported lazily inside `embed_chunk()` so that the
    provider can be imported without requiring the package to be installed.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `OPENAI_API_KEY` is not set.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("OPENAI_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "openai"

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use."""
        return self._model

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters."""
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured OpenAI embedding model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the OpenAI API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            from openai import AsyncOpenAI  # lazy import

            client = AsyncOpenAI(api_key=self._api_key)
            response = await asyncio.wait_for(
                client.embeddings.create(model=self._model, input=text),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(response.data[0].embedding)
        except Exception as exc:
            raise EmbeddingError(f"OpenAI embedding failed (model={self._model}): {exc}") from exc
````

## File: src/mcp_project_context_server/integrations/embeddings/registry.py
````python
"""Embedding provider registry — factory driven by the `EMBED_PROVIDER` env var.

Design rules
------------
* **Fail fast at startup** if `EMBED_PROVIDER` is not set or the value is
  unrecognised.  There is no silent fallback to Ollama or any other provider.
  Explicit configuration is required.
* Importing this module does **not** initialise any provider.  Call
  `get_embedding_provider()` to obtain a provider instance.
* The returned instance is cached after the first call so that repeated
  calls within a process return the same object.

Usage
-----
::

    from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider

    provider = get_embedding_provider()
    vector = await provider.embed("some text")

Supported `EMBED_PROVIDER` values
------------------------------------
`ollama`
    Local Ollama server.  Requires `OLLAMA_HOST` (default: http://localhost:11434)
    and optionally `OLLAMA_EMBED_MODEL` (default: nomic-embed-text).

`voyage`
    Voyage AI cloud API.  Requires `VOYAGE_API_KEY`.
    Optional: `VOYAGE_EMBED_MODEL` (default: voyage-code-3).

`openai`
    OpenAI cloud API.  Requires `OPENAI_API_KEY`.
    Optional: `OPENAI_EMBED_MODEL` (default: text-embedding-3-small).

`cohere`
    Cohere cloud API.  Requires `COHERE_API_KEY`.
    Optional: `COHERE_EMBED_MODEL` (default: embed-english-v3.0).

`google`
    Google Gemini API (google-generativeai).  Requires `GOOGLE_API_KEY`.
    Optional: `GOOGLE_EMBED_MODEL` (default: text-embedding-004).

`vertexai`
    Google Vertex AI.  Requires `GOOGLE_VERTEX_PROJECT` and
    `GOOGLE_VERTEX_LOCATION`.
    Optional: `GOOGLE_VERTEX_EMBED_MODEL` (default: text-embedding-004).
"""
import logging
import os

from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"ollama", "voyage", "openai", "cohere", "google", "vertexai"})


def get_embedding_provider() -> EmbeddingProvider:
    """Return the configured embedding provider singleton.

    :return: (EmbeddingProvider) The embedding provider instance selected by
        the ``EMBED_PROVIDER`` environment variable.
    :raises EnvironmentError: If ``EMBED_PROVIDER`` is not set or is not one of
        the supported provider names.
    :raises ImportError: If the required package for the selected provider is
        not installed.
    """
    provider_name = os.getenv("EMBED_PROVIDER", "").strip().lower()

    if not provider_name:
        raise EnvironmentError(
            "EMBED_PROVIDER environment variable is not set.  "
            f"Set it to one of: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported EMBED_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    provider_instance = _build_provider(provider_name)
    return provider_instance


def _build_provider(provider_name: str) -> EmbeddingProvider:
    """Instantiate and return the provider for *provider_name*."""
    if provider_name == "ollama":
        from mcp_project_context_server.integrations.embeddings.ollama.client import (
            OllamaEmbeddingProvider,
        )

        return OllamaEmbeddingProvider()

    elif provider_name == "voyage":
        from mcp_project_context_server.integrations.embeddings.voyage.client import (
            VoyageEmbeddingProvider,
        )

        return VoyageEmbeddingProvider()

    elif provider_name == "openai":
        from mcp_project_context_server.integrations.embeddings.openai.client import (
            OpenAIEmbeddingProvider,
        )

        return OpenAIEmbeddingProvider()

    elif provider_name == "cohere":
        from mcp_project_context_server.integrations.embeddings.cohere.client import (
            CohereEmbeddingProvider,
        )

        return CohereEmbeddingProvider()

    elif provider_name == "google":
        from mcp_project_context_server.integrations.embeddings.google.client import (
            GoogleEmbeddingProvider,
        )

        return GoogleEmbeddingProvider()

    elif provider_name == "vertexai":
        from mcp_project_context_server.integrations.embeddings.vertexai.client import (
            GoogleVertexEmbeddingProvider,
        )

        return GoogleVertexEmbeddingProvider()

    else:
        # Should never reach here — guarded by the caller.
        raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover
````

## File: src/mcp_project_context_server/integrations/embeddings/voyage/client.py
````python
"""Voyage AI embedding provider — implements the EmbeddingProvider Protocol.

Configuration
-------------
Set these environment variables to control the provider:

`VOYAGE_API_KEY`
    API key for the Voyage AI service.  **Required.**

`VOYAGE_EMBED_MODEL`
    Name of the embedding model to use.  Defaults to `voyage-code-3`.
"""

import asyncio
import logging
import os

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.integrations.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

_DEFAULT_MODEL: str = "voyage-code-3"
# voyage-code-3 context ≈ 32k tokens; conservative character limit
_MAX_CHARS: int = 24_000
_EMBED_TIMEOUT_SECONDS: float = 60.0


class VoyageEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by the Voyage AI API.

    The `voyageai` package is imported lazily inside `embed_chunk()` so that the
    provider can be imported without requiring the package to be installed.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading configuration from environment variables.

        :raises EnvironmentError: If `VOYAGE_API_KEY` is not set.
        """
        api_key = os.getenv("VOYAGE_API_KEY")
        if not api_key:
            raise EnvironmentError("VOYAGE_API_KEY environment variable is not set.")
        self._api_key: str = api_key
        self._model: str = os.getenv("VOYAGE_EMBED_MODEL", _DEFAULT_MODEL)

    # ------------------------------------------------------------------
    # EmbeddingProvider Protocol properties
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        """Short identifier for this provider."""
        return "voyage"

    @property
    def model_name(self) -> str:
        """Name of the embedding model in use."""
        return self._model

    @property
    def max_chars(self) -> int:
        """Approximate maximum input length in characters."""
        return _MAX_CHARS

    # ------------------------------------------------------------------
    # Core embedding method
    # ------------------------------------------------------------------

    async def embed_chunk(self, text: str) -> list[float]:
        """Embed *text* using the configured Voyage AI model.

        :param text: (str) Text to embed. Should be at most `max_chars` long.
        :return: (list) Embedding vector as a list of floats.
        :raises EmbeddingError: If the Voyage AI API returns an error, is
            unreachable, or does not respond within the timeout.
        """
        try:
            import voyageai  # lazy import

            client = voyageai.AsyncClient(api_key=self._api_key)
            result = await asyncio.wait_for(
                client.embed([text], model=self._model, input_type="document"),
                timeout=_EMBED_TIMEOUT_SECONDS,
            )
            return list(result.embeddings[0])
        except Exception as exc:
            raise EmbeddingError(f"Voyage AI embedding failed (model={self._model}): {exc}") from exc
````

## File: src/mcp_project_context_server/integrations/repository/base.py
````python
"""RepositoryProvider Protocol and shared data types."""
import logging
from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class RepositoryInfo:
    """Metadata about a single repository."""

    identifier: str  # e.g. "DarkMatterProductions/vs-cartographytable"
    name: str
    description: str
    indexed: bool  # True if a vector collection exists for this repo
    last_indexed: Optional[str] = None  # ISO datetime string or None


@runtime_checkable
class RepositoryProvider(Protocol):
    """Protocol that all repository provider implementations must satisfy."""

    @property
    def provider_name(self) -> str:
        """Short identifier, e.g. ``"local"``, ``"github"``, ``"gitlab"``, ``"gitea"``."""
        ...

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the .context/ directory of the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (dict) A mapping of relative markdown file paths to their contents.
        """
        ...

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of .context/BUNDLE.md, or None if it does not exist.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (str) The contents of ``.context/BUNDLE.md``, or ``None`` if it does not exist.
        """
        ...

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files from the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (dict) A mapping of relative source file paths to their contents.
        """
        ...

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Write (create or update) a file in the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :param path: (str) The path of the file to write, relative to the repository root.
        :param content: (str) The new full contents of the file.
        :param message: (str) The commit message describing the write.
        :param branch: (str) Target branch. Falls back to the provider's default
            branch when ``None``. Ignored by the local provider.
        :return: (None) This method does not return a value.
        """
        ...

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* from *from_branch* (or the default branch).

        A no-op for the local provider, which has no notion of a remote ref.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :param new_branch: (str) The name of the branch to create.
        :param from_branch: (str) The branch to base the new branch on. Falls back to the
            repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        """
        ...

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch name for the repository.

        :param repo_id: (str) The ``owner/repo`` identifier (or equivalent) of the repository.
        :return: (str) The name of the repository's default branch.
        """
        ...

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible via this provider.

        :param org: (str) Optional organisation/group name to filter results by.
        :return: (list) The accessible ``RepositoryInfo`` entries, optionally filtered by ``org``.
        """
        ...


class RepositoryError(Exception):
    """Raised when a repository provider operation fails."""


def normalize_repo_identifier(raw: str) -> str:
    """Normalise a repo identifier to ``owner/repo`` form.

    Accepts a full ``http(s)://`` URL (the last two path segments are
    extracted and joined) or an already-short ``owner/repo`` identifier
    (returned unchanged).

    :param raw: (str) A full repository URL or a short ``owner/repo`` identifier.
    :return: (str) The normalised ``owner/repo`` identifier.
    """
    if raw.startswith("http://") or raw.startswith("https://"):
        parts = urlparse(raw).path.strip("/").split("/")
        return "/".join(parts[-2:])
    return raw
````

## File: src/mcp_project_context_server/integrations/repository/gitea/client.py
````python
"""Gitea repository provider implementation using the Gitea REST API."""

import base64
import logging
import os
from typing import Optional

import httpx

from mcp_project_context_server.integrations.repository.base import (
    RepositoryError,
    RepositoryInfo,
    normalize_repo_identifier,
)

logger = logging.getLogger(__name__)

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_MAX_SOURCE_FILES = 200


class GiteaRepositoryProvider:
    """Repository provider that communicates with a self-hosted Gitea instance.

    Configuration is read from environment variables at instantiation time:

    * ``REPO_AUTH_TOKEN`` — Gitea access token.
    * ``REPO_BASE_URL`` — **Required** Gitea instance URL (no default).
      The API base is derived as ``{REPO_BASE_URL}/api/v1``.
    * ``REPO_DEFAULT_BRANCH`` — Fallback branch name (default: ``"main"``).
    """

    def __init__(self) -> None:
        """Initialize the provider from environment variables.

        :raises EnvironmentError: If ``REPO_BASE_URL`` is not set.
        """
        self._token: str = os.getenv("REPO_AUTH_TOKEN", "")
        base = os.getenv("REPO_BASE_URL", "").rstrip("/")
        if not base:
            raise EnvironmentError(
                "REPO_BASE_URL is required for the Gitea provider. "
                "Set it to your Gitea instance URL (e.g. https://gitea.example.com)."
            )
        self._api_base: str = f"{base}/api/v1"
        self._default_branch_fallback: str = os.getenv("REPO_DEFAULT_BRANCH", "main")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "gitea"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalise_repo_id(self, repo_id: str) -> str:
        """Normalise *repo_id* to ``owner/repo`` form."""
        return normalize_repo_identifier(repo_id)

    def _headers(self) -> dict[str, str]:
        """Return HTTP headers for Gitea API requests."""
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"token {self._token}"
        return headers

    def _split(self, repo_id: str) -> tuple[str, str]:
        """Return *(owner, repo)* from a normalised ``owner/repo`` string."""
        owner, repo = self._normalise_repo_id(repo_id).split("/", 1)
        return owner, repo

    # ------------------------------------------------------------------
    # Protocol methods
    # ------------------------------------------------------------------

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the ``.context/`` subtree of the repository.

        Returns an empty dict on 404.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative markdown file paths to their contents.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                headers=self._headers(),
            )
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            tree = resp.json().get("tree", [])
            for item in tree:
                path: str = item.get("path", "")
                if path.startswith(".context/") and path.endswith(".md"):
                    rel = path.removeprefix(".context/")
                    raw = await client.get(
                        f"{self._api_base}/repos/{owner}/{repo}/raw/.context/{rel}" f"?ref={branch}",
                        headers=self._headers(),
                    )
                    if raw.status_code == 200:
                        result[rel] = raw.text
        return result

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of ``.context/BUNDLE.md``, or ``None``.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (str) The contents of ``BUNDLE.md``, or ``None`` if it does not exist.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/raw/.context/BUNDLE.md?ref={branch}",
                headers=self._headers(),
            )
            if resp.status_code == 200:
                return resp.text
            return None

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files from the repository tree.

        Capped at 200 files.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative source file paths to their contents.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                headers=self._headers(),
            )
            resp.raise_for_status()
            tree = resp.json().get("tree", [])
            candidates = [item for item in tree if _has_source_extension(item.get("path", ""))][:_MAX_SOURCE_FILES]
            for item in candidates:
                path = item["path"]
                raw = await client.get(
                    f"{self._api_base}/repos/{owner}/{repo}/raw/{path}?ref={branch}",
                    headers=self._headers(),
                )
                if raw.status_code == 200:
                    result[path] = raw.text
        return result

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Create or update *path* in the repository.

        Writes to *branch* if given, otherwise the repository's default
        branch.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :param path: (str) The file path to write, relative to the repository root.
        :param content: (str) The new full contents of the file.
        :param message: (str) The commit message describing the write.
        :param branch: (str) Target branch. Falls back to the repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        owner, repo = self._split(repo_id)
        target_branch = branch or await self.get_default_branch(repo_id)
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        async with httpx.AsyncClient() as client:
            # Check if file exists to get SHA — must be scoped to the target
            # branch, otherwise this always reads the default branch's SHA.
            check = await client.get(
                f"{self._api_base}/repos/{owner}/{repo}/contents/{path}",
                headers=self._headers(),
                params={"ref": target_branch},
            )
            if check.status_code == 200:
                sha = check.json().get("sha", "")
                payload = {"message": message, "content": encoded, "sha": sha, "branch": target_branch}
                resp = await client.patch(
                    f"{self._api_base}/repos/{owner}/{repo}/contents/{path}",
                    headers=self._headers(),
                    json=payload,
                )
            else:
                payload = {"message": message, "content": encoded, "branch": target_branch}
                resp = await client.post(
                    f"{self._api_base}/repos/{owner}/{repo}/contents/{path}",
                    headers=self._headers(),
                    json=payload,
                )
            if not resp.is_success:
                raise RepositoryError(f"Gitea write_file failed ({resp.status_code}): {resp.text}")

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* from *from_branch* (or the default branch).

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :param new_branch: (str) The name of the branch to create.
        :param from_branch: (str) The branch to base the new branch on. Falls back to the
            repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        owner, repo = self._split(repo_id)
        base = from_branch or await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._api_base}/repos/{owner}/{repo}/branches",
                headers=self._headers(),
                json={"new_branch_name": new_branch, "old_branch_name": base},
            )
            if not resp.is_success:
                raise RepositoryError(f"Gitea create_branch failed ({resp.status_code}): {resp.text}")

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch for *repo_id*, falling back to env / ``"main"``.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (str) The repository's default branch name, or the configured/``"main"`` fallback.
        """
        owner, repo = self._split(repo_id)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._api_base}/repos/{owner}/{repo}",
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    return resp.json().get("default_branch", self._default_branch_fallback)
        except Exception:
            pass
        return self._default_branch_fallback

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible to the configured token.

        If *org* is set, lists repositories for that organisation.  Otherwise
        searches all accessible repositories.

        :param org: (str) Optional organisation name to list repositories for.
        :return: (list) The accessible ``RepositoryInfo`` entries.
        """
        async with httpx.AsyncClient() as client:
            if org:
                url = f"{self._api_base}/orgs/{org}/repos"
            else:
                params = "limit=50"
                if self._token:
                    params += f"&token={self._token}"
                url = f"{self._api_base}/repos/search?{params}"
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            # /repos/search returns {"data": [...]} while /orgs/{org}/repos returns [...]
            items = data.get("data", data) if isinstance(data, dict) else data
            return [_repo_info_from_gitea(r) for r in items]


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _has_source_extension(path: str) -> bool:
    """Return True if *path* ends with a recognised source extension."""
    return any(path.endswith(ext) for ext in _SOURCE_EXTENSIONS)


def _repo_info_from_gitea(data: dict) -> RepositoryInfo:
    """Build a :class:`RepositoryInfo` from a Gitea API repository object."""
    return RepositoryInfo(
        identifier=data.get("full_name", ""),
        name=data.get("name", ""),
        description=data.get("description") or "",
        indexed=False,
    )
````

## File: src/mcp_project_context_server/integrations/repository/github/client.py
````python
"""GitHub repository provider implementation using the GitHub REST API."""

import base64
import logging
import os
from typing import Optional

import httpx

from mcp_project_context_server.integrations.repository.base import (
    RepositoryError,
    RepositoryInfo,
    normalize_repo_identifier,
)

logger = logging.getLogger(__name__)

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_MAX_SOURCE_FILES = 200


class GitHubRepositoryProvider:
    """Repository provider that communicates with the GitHub REST API.

    Configuration is read from environment variables at instantiation time:

    * ``REPO_AUTH_TOKEN`` — GitHub personal access token (required for private repos).
    * ``REPO_BASE_URL`` — Base URL for GitHub Enterprise (default: ``https://api.github.com``).
    * ``REPO_DEFAULT_BRANCH`` — Fallback branch name when the API cannot be reached
      (default: ``"main"``).
    """

    def __init__(self) -> None:
        """Initialize the provider from environment variables."""
        self._token: str = os.getenv("GITHUB_TOKEN", "")
        self._base_url: str = os.getenv("REPO_BASE_URL", "https://api.github.com").rstrip("/")
        self._default_branch_fallback: str = os.getenv("REPO_DEFAULT_BRANCH", "main")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "github"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalise_repo_id(self, repo_id: str) -> str:
        """Normalise *repo_id* to the ``owner/repo`` form.

        If *repo_id* starts with ``http://`` or ``https://`` the last two path
        segments are extracted and joined.  Otherwise the value is returned as-is.
        """
        return normalize_repo_identifier(repo_id)

    def _headers(self) -> dict[str, str]:
        """Return HTTP headers for GitHub API requests."""
        headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _split(self, repo_id: str) -> tuple[str, str]:
        """Return *(owner, repo)* from a normalised ``owner/repo`` string."""
        owner, repo = self._normalise_repo_id(repo_id).split("/", 1)
        return owner, repo

    # ------------------------------------------------------------------
    # Protocol methods
    # ------------------------------------------------------------------

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the ``.context/`` directory of the repository.

        Returns an empty dict on 404.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative markdown file paths to their contents.
        """
        owner, repo = self._split(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/contents/.context",
                headers=self._headers(),
            )
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            items = resp.json()
            await _collect_github_md_files(client, items, self._headers(), ".context", result)
        return result

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of ``.context/BUNDLE.md``, or ``None``.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (str) The contents of ``BUNDLE.md``, or ``None`` if it does not exist.
        """
        owner, repo = self._split(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/contents/.context/BUNDLE.md",
                headers=self._headers(),
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            download_url = data.get("download_url")
            if not download_url:
                return None
            raw = await client.get(download_url, headers=self._headers())
            return raw.text

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files via the Git Trees API.

        Capped at 200 files.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative source file paths to their contents.
        """
        owner, repo = self._split(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                headers=self._headers(),
            )
            resp.raise_for_status()
            tree = resp.json().get("tree", [])
            candidates = [
                item for item in tree if item.get("type") == "blob" and _has_source_extension(item.get("path", ""))
            ][:_MAX_SOURCE_FILES]
            for item in candidates:
                path = item["path"]
                raw_resp = await client.get(
                    f"{self._base_url}/repos/{owner}/{repo}/contents/{path}",
                    headers=self._headers(),
                )
                if raw_resp.status_code == 200:
                    data = raw_resp.json()
                    if data.get("encoding") == "base64":
                        result[path] = base64.b64decode(data["content"].replace("\n", "")).decode(
                            "utf-8", errors="replace"
                        )
        return result

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Create or update *path* in the repository.

        Writes to *branch* if given, otherwise the repository's default
        branch.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :param path: (str) The file path to write, relative to the repository root.
        :param content: (str) The new full contents of the file.
        :param message: (str) The commit message describing the write.
        :param branch: (str) Target branch. Falls back to the repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        owner, repo = self._split(repo_id)
        target_branch = branch or await self.get_default_branch(repo_id)
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        async with httpx.AsyncClient() as client:
            # Check for existing file SHA on the target branch specifically —
            # without ?ref= this would always read the default branch's SHA,
            # which is wrong once writes can target other branches.
            sha: Optional[str] = None
            check = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._headers(),
                params={"ref": target_branch},
            )
            if check.status_code == 200:
                sha = check.json().get("sha")

            payload: dict = {"message": message, "content": encoded, "branch": target_branch}
            if sha:
                payload["sha"] = sha

            resp = await client.put(
                f"{self._base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._headers(),
                json=payload,
            )
            if not resp.is_success:
                raise RepositoryError(f"GitHub write_file failed ({resp.status_code}): {resp.text}")

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* pointing at the tip of *from_branch* (or the default branch).

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :param new_branch: (str) The name of the branch to create.
        :param from_branch: (str) The branch to base the new branch on. Falls back to the
            repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the base ref cannot be resolved or the
            API returns a non-success status when creating the new ref.
        """
        owner, repo = self._split(repo_id)
        base = from_branch or await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            ref_resp = await client.get(
                f"{self._base_url}/repos/{owner}/{repo}/git/ref/heads/{base}",
                headers=self._headers(),
            )
            if not ref_resp.is_success:
                raise RepositoryError(
                    f"GitHub create_branch failed to resolve base branch '{base}' "
                    f"({ref_resp.status_code}): {ref_resp.text}"
                )
            sha = ref_resp.json()["object"]["sha"]

            resp = await client.post(
                f"{self._base_url}/repos/{owner}/{repo}/git/refs",
                headers=self._headers(),
                json={"ref": f"refs/heads/{new_branch}", "sha": sha},
            )
            if not resp.is_success:
                raise RepositoryError(f"GitHub create_branch failed ({resp.status_code}): {resp.text}")

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch for *repo_id*, falling back to env / ``"main"``.

        :param repo_id: (str) The ``owner/repo`` identifier or full URL of the repository.
        :return: (str) The repository's default branch name, or the configured/``"main"`` fallback.
        """
        owner, repo = self._split(repo_id)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._base_url}/repos/{owner}/{repo}",
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    return resp.json().get("default_branch", self._default_branch_fallback)
        except Exception:
            pass
        return self._default_branch_fallback

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible to the configured token.

        If *org* is set, lists repositories for that organisation.  Otherwise
        lists the authenticated user's repositories.

        :param org: (str) Optional organisation name to list repositories for.
        :return: (list) The accessible ``RepositoryInfo`` entries.
        """
        async with httpx.AsyncClient() as client:
            if org:
                url = f"{self._base_url}/orgs/{org}/repos?per_page=100"
            else:
                url = f"{self._base_url}/user/repos?per_page=100"
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return [_repo_info_from_github(r) for r in resp.json()]


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _has_source_extension(path: str) -> bool:
    """Return True if *path* ends with a recognised source extension."""
    return any(path.endswith(ext) for ext in _SOURCE_EXTENSIONS)


async def _collect_github_md_files(
    client: httpx.AsyncClient,
    items: list,
    headers: dict,
    prefix: str,
    result: dict,
) -> None:
    """Recursively collect .md files from a GitHub contents listing."""
    for item in items:
        if item.get("type") == "file" and item["name"].endswith(".md"):
            download_url = item.get("download_url")
            if download_url:
                raw = await client.get(download_url, headers=headers)
                if raw.status_code == 200:
                    rel_path = item["path"].removeprefix(prefix + "/")
                    result[rel_path] = raw.text
        elif item.get("type") == "dir":
            sub = await client.get(item["url"], headers=headers)
            if sub.status_code == 200:
                await _collect_github_md_files(client, sub.json(), headers, prefix, result)


def _repo_info_from_github(data: dict) -> RepositoryInfo:
    """Build a :class:`RepositoryInfo` from a GitHub API repository object."""
    return RepositoryInfo(
        identifier=data.get("full_name", ""),
        name=data.get("name", ""),
        description=data.get("description") or "",
        indexed=False,
    )
````

## File: src/mcp_project_context_server/integrations/repository/gitlab/client.py
````python
"""GitLab repository provider implementation using the GitLab REST API."""
import logging
import os
from typing import Optional
from urllib.parse import quote

import httpx

from mcp_project_context_server.integrations.repository.base import (
    RepositoryError,
    RepositoryInfo,
    normalize_repo_identifier,
)

logger = logging.getLogger(__name__)

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_MAX_SOURCE_FILES = 200


class GitLabRepositoryProvider:
    """Repository provider that communicates with the GitLab REST API (v4).

    Configuration is read from environment variables at instantiation time:

    * ``REPO_AUTH_TOKEN`` — GitLab personal access token.
    * ``REPO_BASE_URL`` — GitLab instance URL (default: ``https://gitlab.com``).
      The API base is derived as ``{REPO_BASE_URL}/api/v4``.
    * ``REPO_DEFAULT_BRANCH`` — Fallback branch name (default: ``"main"``).
    """

    def __init__(self) -> None:
        """Initialize the provider from environment variables."""
        self._token: str = os.getenv("REPO_AUTH_TOKEN", "")
        base = os.getenv("REPO_BASE_URL", "https://gitlab.com").rstrip("/")
        self._api_base: str = f"{base}/api/v4"
        self._default_branch_fallback: str = os.getenv("REPO_DEFAULT_BRANCH", "main")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "gitlab"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalise_repo_id(self, repo_id: str) -> str:
        """Normalise *repo_id* to ``namespace/project`` form."""
        return normalize_repo_identifier(repo_id)

    def _url_encode_id(self, repo_id: str) -> str:
        """URL-encode the ``namespace/project`` string for GitLab's ``:id`` parameter."""
        return quote(self._normalise_repo_id(repo_id), safe="")

    def _headers(self) -> dict[str, str]:
        """Return HTTP headers for GitLab API requests."""
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["PRIVATE-TOKEN"] = self._token
        return headers

    # ------------------------------------------------------------------
    # Protocol methods
    # ------------------------------------------------------------------

    async def fetch_context_files(self, repo_id: str) -> dict[str, str]:
        """Fetch all .md files from the ``.context/`` tree of the repository.

        Returns an empty dict on 404.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative markdown file paths to their contents.
        """
        encoded_id = self._url_encode_id(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/projects/{encoded_id}/repository/tree"
                f"?path=.context&recursive=true&ref={branch}&per_page=100",
                headers=self._headers(),
            )
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            for item in resp.json():
                if item.get("type") == "blob" and item["name"].endswith(".md"):
                    file_path = item["path"]
                    encoded_path = quote(file_path, safe="")
                    raw = await client.get(
                        f"{self._api_base}/projects/{encoded_id}/repository/files" f"/{encoded_path}/raw?ref={branch}",
                        headers=self._headers(),
                    )
                    if raw.status_code == 200:
                        rel = file_path.removeprefix(".context/")
                        result[rel] = raw.text
        return result

    async def fetch_source_bundle(self, repo_id: str) -> Optional[str]:
        """Fetch the content of ``.context/BUNDLE.md``, or ``None``.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (str) The contents of ``BUNDLE.md``, or ``None`` if it does not exist.
        """
        encoded_id = self._url_encode_id(repo_id)
        branch = await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/projects/{encoded_id}/repository/files" f"/.context%2FBUNDLE.md/raw?ref={branch}",
                headers=self._headers(),
            )
            if resp.status_code == 200:
                return resp.text
            return None

    async def fetch_source_files(self, repo_id: str) -> dict[str, str]:
        """Fetch source code files from the repository tree.

        Capped at 200 files.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (dict) A mapping of relative source file paths to their contents.
        """
        encoded_id = self._url_encode_id(repo_id)
        branch = await self.get_default_branch(repo_id)
        result: dict[str, str] = {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._api_base}/projects/{encoded_id}/repository/tree" f"?recursive=true&ref={branch}&per_page=100",
                headers=self._headers(),
            )
            resp.raise_for_status()
            candidates = [
                item
                for item in resp.json()
                if item.get("type") == "blob" and _has_source_extension(item.get("path", ""))
            ][:_MAX_SOURCE_FILES]
            for item in candidates:
                path = item["path"]
                encoded_path = quote(path, safe="")
                raw = await client.get(
                    f"{self._api_base}/projects/{encoded_id}/repository/files" f"/{encoded_path}/raw?ref={branch}",
                    headers=self._headers(),
                )
                if raw.status_code == 200:
                    result[path] = raw.text
        return result

    async def write_file(
        self, repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Create or update *path* in the repository.

        Writes to *branch* if given, otherwise the repository's default
        branch.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :param path: (str) The file path to write, relative to the repository root.
        :param content: (str) The new full contents of the file.
        :param message: (str) The commit message describing the write.
        :param branch: (str) Target branch. Falls back to the repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        encoded_id = self._url_encode_id(repo_id)
        target_branch = branch or await self.get_default_branch(repo_id)
        encoded_path = quote(path, safe="")
        payload = {"branch": target_branch, "content": content, "commit_message": message}
        async with httpx.AsyncClient() as client:
            # Check if file exists
            head = await client.head(
                f"{self._api_base}/projects/{encoded_id}/repository/files/{encoded_path}" f"?ref={target_branch}",
                headers=self._headers(),
            )
            if head.status_code == 200:
                method = client.put
            else:
                method = client.post
            resp = await method(
                f"{self._api_base}/projects/{encoded_id}/repository/files/{encoded_path}",
                headers=self._headers(),
                json=payload,
            )
            if not resp.is_success:
                raise RepositoryError(f"GitLab write_file failed ({resp.status_code}): {resp.text}")

    async def create_branch(self, repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """Create *new_branch* from *from_branch* (or the default branch).

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :param new_branch: (str) The name of the branch to create.
        :param from_branch: (str) The branch to base the new branch on. Falls back to the
            repository's default branch when ``None``.
        :return: (None) This method does not return a value.
        :raises RepositoryError: If the API returns a non-success status.
        """
        encoded_id = self._url_encode_id(repo_id)
        base = from_branch or await self.get_default_branch(repo_id)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._api_base}/projects/{encoded_id}/repository/branches",
                headers=self._headers(),
                params={"branch": new_branch, "ref": base},
            )
            if not resp.is_success:
                raise RepositoryError(f"GitLab create_branch failed ({resp.status_code}): {resp.text}")

    async def get_default_branch(self, repo_id: str) -> str:
        """Return the default branch for *repo_id*, falling back to env / ``"main"``.

        :param repo_id: (str) The ``namespace/project`` identifier or full URL of the repository.
        :return: (str) The repository's default branch name, or the configured/``"main"`` fallback.
        """
        encoded_id = self._url_encode_id(repo_id)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._api_base}/projects/{encoded_id}",
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    return resp.json().get("default_branch", self._default_branch_fallback)
        except Exception:
            pass
        return self._default_branch_fallback

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """List repositories accessible to the configured token.

        If *org* is set, lists projects for that GitLab group.  Otherwise lists
        all projects the authenticated user is a member of.

        :param org: (str) Optional GitLab group name to list projects for.
        :return: (list) The accessible ``RepositoryInfo`` entries.
        """
        async with httpx.AsyncClient() as client:
            if org:
                url = f"{self._api_base}/groups/{org}/projects?per_page=100"
            else:
                url = f"{self._api_base}/projects?membership=true&per_page=100"
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return [_repo_info_from_gitlab(r) for r in resp.json()]


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _has_source_extension(path: str) -> bool:
    """Return True if *path* ends with a recognised source extension."""
    return any(path.endswith(ext) for ext in _SOURCE_EXTENSIONS)


def _repo_info_from_gitlab(data: dict) -> RepositoryInfo:
    """Build a :class:`RepositoryInfo` from a GitLab API project object."""
    namespace = data.get("namespace", {}).get("full_path", "")
    name = data.get("name", "")
    identifier = f"{namespace}/{name}" if namespace else name
    return RepositoryInfo(
        identifier=identifier,
        name=name,
        description=data.get("description") or "",
        indexed=False,
    )
````

## File: src/mcp_project_context_server/integrations/repository/local/client.py
````python
"""Local filesystem repository provider implementation."""

import asyncio
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

from mcp_project_context_server.integrations.repository.base import RepositoryInfo

logger = logging.getLogger(__name__)

_SOURCE_EXTENSIONS: frozenset[str] = frozenset({".py", ".ts", ".js", ".go", ".rs", ".cs", ".java", ".rb", ".php"})
_SKIP_DIRS: frozenset[str] = frozenset({".git", "node_modules", ".venv", "__pycache__", "dist", "build"})
_MAX_SOURCE_FILES = 500


class LocalRepositoryProvider:
    """Repository provider that reads from the local filesystem.

    ``repo_id`` for all methods is always a filesystem path (str or Path).
    """

    def __init__(self) -> None:
        """Initialize the provider, reading PROJECT_PATH from the environment."""
        self._project_path: str = os.getenv("PROJECT_PATH", "")

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "local"

    @staticmethod
    async def fetch_context_files(repo_id: str) -> dict[str, str]:
        """Read all .md files from ``<repo_id>/.context/`` recursively.

        Returns a dict keyed by POSIX relative paths.  Returns an empty dict if
        the ``.context/`` directory does not exist.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (dict) A mapping of POSIX-style relative markdown file paths to their contents.
        """
        logger.debug(f"Executing 'fetch_context_files' with the arguments repo_id: {repo_id}")
        context_dir = Path(repo_id) / ".context"
        if not context_dir.is_dir():
            return {}
        result: dict[str, str] = {}
        for md_file in context_dir.rglob("*.md"):
            key = md_file.relative_to(context_dir).as_posix()
            result[key] = md_file.read_text(encoding="utf-8")
        return result

    @staticmethod
    async def fetch_source_bundle(repo_id: str) -> Optional[str]:
        """Return the content of ``<repo_id>/.context/BUNDLE.md``, or None.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (str) The contents of ``BUNDLE.md``, or ``None`` if it does not exist.
        """
        logger.debug(f"Executing 'fetch_source_bundle' with the arguments repo_id: {repo_id}")
        bundle = Path(repo_id) / ".context" / "BUNDLE.md"
        if bundle.is_file():
            return bundle.read_text(encoding="utf-8")
        return None

    @staticmethod
    async def fetch_source_files(repo_id: str) -> dict[str, str]:
        """Return source code files under ``repo_id``, skipping common non-source dirs.

        Capped at ``_MAX_SOURCE_FILES`` (500) entries.  Keys are POSIX paths
        relative to ``repo_id``.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (dict) A mapping of POSIX-style relative source file paths to their contents.
        """
        logger.debug(f"Executing 'fetch_source_files' with the arguments repo_id: {repo_id}")
        root = Path(repo_id)
        result: dict[str, str] = {}
        for file_path in _walk_source_files(root):
            if len(result) >= _MAX_SOURCE_FILES:
                break
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            key = file_path.relative_to(root).as_posix()
            result[key] = content
        return result

    @staticmethod
    async def write_file(
        repo_id: str, path: str, content: str, message: str, branch: Optional[str] = None
    ) -> None:
        """Write ``content`` to ``<repo_id>/<path>``, creating parent directories.

        ``message`` and ``branch`` are ignored for the local provider (no
        commit is made; writes always land on whatever is checked out).

        :param repo_id: (str) Filesystem path to the project root.
        :param path: (str) The file path to write, relative to ``repo_id``.
        :param content: (str) The new full contents of the file.
        :param message: (str) Ignored by the local provider.
        :param branch: (str) Ignored by the local provider.
        :return: (None) This method does not return a value.
        """
        logger.debug(f"Executing 'write_file' with the arguments repo_id: {repo_id}, path: {path}, content: {content}, message: {message}, branch: {branch}")
        target = Path(repo_id) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    @staticmethod
    async def create_branch(repo_id: str, new_branch: str, from_branch: Optional[str] = None) -> None:
        """No-op: the local provider writes directly to disk regardless of branch.

        :param repo_id: (str) Filesystem path to the project root.
        :param new_branch: (str) Ignored by the local provider.
        :param from_branch: (str) Ignored by the local provider.
        :return: (None) This method does not return a value.
        """
        logger.debug(f"Executing 'create_branch' with the arguments repo_id: {repo_id}, new_branch: {new_branch}, from_branch: {from_branch}")
        return None

    @staticmethod
    async def get_default_branch(repo_id: str) -> str:
        """Return the current git branch for the repository, falling back to ``"main"``.

        :param repo_id: (str) Filesystem path to the project root.
        :return: (str) The current git branch name, or ``"main"`` if it cannot be determined.
        """
        logger.debug(f"Executing 'get_default_branch' with the arguments repo_id: {repo_id}")

        def _run_git() -> str:
            result = subprocess.run(
                ["git", "-C", str(repo_id), "symbolic-ref", "--short", "HEAD"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "main"

        return await asyncio.to_thread(_run_git)

    async def list_repositories(self, org: Optional[str] = None) -> list[RepositoryInfo]:
        """Return a single-element list for the project path from ``PROJECT_PATH``.

        Returns an empty list if ``PROJECT_PATH`` is not set.  ``org`` is ignored
        for the local provider.

        :param org: (str) Ignored by the local provider.
        :return: (list) A single-element list describing the ``PROJECT_PATH`` project,
            or an empty list if ``PROJECT_PATH`` is not set.
        """
        logger.debug(f"Executing 'list_repositories' with the arguments org: {org}")
        if not self._project_path:
            return []
        p = Path(self._project_path)
        return [
            RepositoryInfo(
                identifier=self._project_path,
                name=p.name,
                description="",
                indexed=False,
            )
        ]


def _walk_source_files(root: Path):
    """Yield source files under *root*, skipping known non-source directories."""
    logger.debug(f"Executing '_walk_source_files' with the arguments org: {root}")
    for entry in root.iterdir():
        if entry.is_dir():
            if entry.name in _SKIP_DIRS:
                continue
            yield from _walk_source_files(entry)
        elif entry.is_file() and entry.suffix in _SOURCE_EXTENSIONS:
            yield entry
````

## File: src/mcp_project_context_server/integrations/repository/registry.py
````python
"""Repository provider registry — factory driven by the ``REPO_PROVIDER`` env var.

Design rules
------------
* Defaults to ``"local"`` when ``REPO_PROVIDER`` is not set.
* **Fail fast** if the value is unrecognised.
* The returned instance is cached after the first call.
* Multi-tenant mode is activated by ``REPO_MULTI_TENANT=true``.

Usage
-----
::

    from mcp_project_context_server.integrations.repository.registry import (
        get_repository_provider,
        validate_repo_access,
    )

    provider = get_repository_provider()
    validate_repo_access("owner/repo")

Supported ``REPO_PROVIDER`` values
------------------------------------
``local``
    Local filesystem provider.

``github``
    GitHub / GitHub Enterprise.

``gitlab``
    GitLab / self-hosted GitLab.

``gitea``
    Self-hosted Gitea.  Requires ``REPO_BASE_URL``.

Multi-tenant mode (``REPO_MULTI_TENANT=true``)
----------------------------------------------
At least one of ``APPROVED_ORGS`` or ``APPROVED_REPOS`` must be set.
``validate_repo_access(repo_id)`` raises :exc:`RepositoryError` if the
repo identifier is not in any approved list.
"""
import logging
import os
from typing import Optional

from mcp_project_context_server.integrations.repository.base import RepositoryError, RepositoryProvider

logger = logging.getLogger(__name__)

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"local", "github", "gitlab", "gitea"})

_provider_instance: Optional[RepositoryProvider] = None

# Multi-tenant state — populated lazily alongside the provider singleton.
_multi_tenant_enabled: bool = False
_approved_orgs: frozenset[str] = frozenset()
_approved_repos: frozenset[str] = frozenset()


def get_repository_provider() -> RepositoryProvider:
    """Return the configured repository provider singleton.

    :return: (RepositoryProvider) The repository provider instance selected by
        the ``REPO_PROVIDER`` environment variable (defaults to ``"local"``).
    :raises EnvironmentError: If ``REPO_PROVIDER`` is set to an unrecognised value,
        or if multi-tenant mode is active but no approved orgs/repos are
        configured.
    """
    global _provider_instance, _multi_tenant_enabled, _approved_orgs, _approved_repos

    if _provider_instance is not None:
        return _provider_instance

    provider_name = os.getenv("REPO_PROVIDER", "local").strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported REPO_PROVIDER value '{provider_name}'. "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    # Multi-tenant setup
    _multi_tenant_enabled = os.getenv("REPO_MULTI_TENANT", "false").strip().lower() == "true"
    if _multi_tenant_enabled:
        orgs_raw = os.getenv("APPROVED_ORGS", "").strip()
        repos_raw = os.getenv("APPROVED_REPOS", "").strip()
        if not orgs_raw and not repos_raw:
            raise EnvironmentError(
                "REPO_MULTI_TENANT=true requires at least one of APPROVED_ORGS or " "APPROVED_REPOS to be set."
            )
        _approved_orgs = frozenset(o.strip() for o in orgs_raw.split(",") if o.strip())
        _approved_repos = frozenset(r.strip() for r in repos_raw.split(",") if r.strip())

    _provider_instance = _build_provider(provider_name)
    return _provider_instance


def _build_provider(provider_name: str) -> RepositoryProvider:
    """Instantiate and return the provider for *provider_name*."""
    if provider_name == "local":
        from mcp_project_context_server.integrations.repository.local.client import (
            LocalRepositoryProvider,
        )

        return LocalRepositoryProvider()

    if provider_name == "github":
        from mcp_project_context_server.integrations.repository.github.client import (
            GitHubRepositoryProvider,
        )

        return GitHubRepositoryProvider()

    if provider_name == "gitlab":
        from mcp_project_context_server.integrations.repository.gitlab.client import (
            GitLabRepositoryProvider,
        )

        return GitLabRepositoryProvider()

    if provider_name == "gitea":
        from mcp_project_context_server.integrations.repository.gitea.client import (
            GiteaRepositoryProvider,
        )

        return GiteaRepositoryProvider()

    # Should never reach here — guarded by the caller.
    raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover


def validate_repo_access(repo_id: str) -> None:
    """Raise :exc:`RepositoryError` if *repo_id* is not in the approved allowlist.

    In single-tenant mode (``REPO_MULTI_TENANT`` unset or ``false``) this is
    always a no-op.

    :param repo_id: (str) The ``owner/repo`` (or equivalent) identifier to validate.
    :return: (None) This function does not return a value.
    :raises RepositoryError: If multi-tenant mode is active, and *repo_id* is not in
        the approved orgs or repos allowlists.
    """
    # Ensure the multi-tenant flags have been populated even if this is the
    # first call into the registry for this process (lazy singleton init).
    get_repository_provider()

    if not _multi_tenant_enabled:
        return

    # Check explicit repo allowlist
    if repo_id in _approved_repos:
        return

    # Check org membership — repo_id is expected to be "org/repo"
    if "/" in repo_id:
        org = repo_id.split("/", 1)[0]
        if org in _approved_orgs:
            return

    raise RepositoryError(
        f"Access to repository '{repo_id}' is not permitted. " "Check APPROVED_ORGS and APPROVED_REPOS configuration."
    )


def reset_provider_for_testing() -> None:
    """Reset the cached provider singleton and multi-tenant state.

    **For use in tests only.**  Call this in test teardown to prevent provider
    state from leaking between test cases.

    :return: (None) This function does not return a value.
    """
    global _provider_instance, _multi_tenant_enabled, _approved_orgs, _approved_repos
    _provider_instance = None
    _multi_tenant_enabled = False
    _approved_orgs = frozenset()
    _approved_repos = frozenset()
````

## File: src/mcp_project_context_server/integrations/vectorstore/base.py
````python
"""VectorStoreProvider Protocol — the provider abstraction boundary for vector storage.

All vector store providers must implement this Protocol so that the rest of the
codebase can depend on the abstraction rather than any concrete backend.

Usage
-----
::

    from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider
    from mcp_project_context_server.integrations.vectorstore.registry import get_vector_store

    store = get_vector_store()
    collection = await store.get_or_create_collection("my-project")
"""
import logging
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Results returned from a vector similarity query."""

    ids: list[str]
    documents: list[str]
    metadatas: list[dict]
    distances: list[float] = field(default_factory=list)


@runtime_checkable
class VectorStoreProvider(Protocol):
    """Protocol that all vector store provider implementations must satisfy.

    Implementations must be safe to import without triggering network connections
    or filesystem I/O — those should be deferred to first method call.
    """

    @property
    def provider_name(self) -> str:
        """Short identifier, e.g. ``"chroma-local"``, ``"pgvector"``."""
        ...

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Create a collection, replacing it if it already exists.

        Implements the drop-and-recreate strategy (ADR-00006): any existing
        collection with *name* is deleted before the new one is created.

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        """
        ...

    async def delete_collection(self, name: str) -> None:
        """Delete a collection.  Silently succeeds if it does not exist.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        ...

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Insert or update documents in a collection.

        :param collection_name: (str) Target collection.
        :param ids: (list) Per-document unique identifiers.
        :param embeddings: (list) Per-document embedding vectors (must all be the same length).
        :param documents: (list) Raw text for each document.
        :param metadatas: (list) Per-document metadata dicts.
        :return: (None) This method does not return a value.
        """
        ...

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run a nearest-neighbour search against a collection.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the collection does not exist or the query fails.
        """
        ...

    async def count(self, collection_name: str) -> int:
        """Return the number of documents stored in *collection_name*.

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        ...

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if *collection_name* exists in this store.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """
        ...

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return the metadata dict stored on a collection.

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection
            does not exist.
        """
        ...


class VectorStoreError(Exception):
    """Raised when a vector store operation fails."""
````

## File: src/mcp_project_context_server/integrations/vectorstore/chroma_http/client.py
````python
"""ChromaDB HTTP (remote) vector store provider.

Configuration
-------------
``CHROMA_HOST``
    Hostname or IP of the ChromaDB server.  Defaults to ``localhost``.

``CHROMA_PORT``
    Port the server listens on.  Defaults to ``8000``.

``CHROMA_API_KEY``
    Optional static API key for ChromaDB's built-in auth.
    Leave unset if the server does not require authentication.
"""

import asyncio
import logging
import os
from typing import Any, Optional

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)

logger = logging.getLogger(__name__)


class ChromaHttpVectorStoreProvider:
    """Vector store backed by a remote ChromaDB HTTP server.

    The chromadb ``HttpClient`` is initialized lazily on first use.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading connection settings from the environment."""
        self._host: str = os.getenv("CHROMA_HOST", "localhost")
        self._port: int = int(os.getenv("CHROMA_PORT", "8000"))
        self._api_key: Optional[str] = os.getenv("CHROMA_API_KEY") or None
        self._client: Optional[Any] = None

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "chroma-http"

    def _get_client(self) -> Any:
        """Return the ChromaDB HTTP client, initialising on first call."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings

            settings = Settings(anonymized_telemetry=False)
            if self._api_key:
                settings = Settings(
                    anonymized_telemetry=False,
                    chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                    chroma_client_auth_credentials=self._api_key,
                )
            self._client = chromadb.HttpClient(
                host=self._host,
                port=self._port,
                settings=settings,
            )
        return self._client

    # ------------------------------------------------------------------
    # VectorStoreProvider Protocol implementation
    # ------------------------------------------------------------------

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Drop and recreate *name* (ADR-00006).

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                client.delete_collection(name)
            except Exception:
                pass
            client.create_collection(name=name, metadata=metadata or {})

        await asyncio.to_thread(_sync)

    async def delete_collection(self, name: str) -> None:
        """Delete *name*, silently succeeding if absent.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                client.delete_collection(name)
            except Exception:
                pass

        await asyncio.to_thread(_sync)

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Add or update documents.

        :param collection_name: (str) Target collection.
        :param ids: (list) Per-document unique identifiers.
        :param embeddings: (list) Per-document embedding vectors (must all be the same length).
        :param documents: (list) Raw text for each document.
        :param metadatas: (list) Per-document metadata dicts.
        :return: (None) This method does not return a value.
        :raises VectorStoreError: If the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                col = client.get_collection(collection_name)
            except Exception as exc:
                raise VectorStoreError(f"Collection '{collection_name}' not found: {exc}") from exc
            col.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

        await asyncio.to_thread(_sync)

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run a nearest-neighbour search.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> QueryResult:
            try:
                col = client.get_collection(collection_name)
            except Exception as exc:
                raise VectorStoreError(f"Collection '{collection_name}' not found: {exc}") from exc
            n = min(n_results, col.count())
            if n == 0:
                return QueryResult(ids=[], documents=[], metadatas=[], distances=[])
            raw = col.query(query_embeddings=[query_embedding], n_results=n)
            return QueryResult(
                ids=raw["ids"][0] if raw.get("ids") else [],
                documents=raw["documents"][0] if raw.get("documents") else [],
                metadatas=raw["metadatas"][0] if raw.get("metadatas") else [],
                distances=raw["distances"][0] if raw.get("distances") else [],
            )

        return await asyncio.to_thread(_sync)

    async def count(self, collection_name: str) -> int:
        """Return document count (0 if collection absent).

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> int:
            try:
                return client.get_collection(collection_name).count()
            except Exception:
                return 0

        return await asyncio.to_thread(_sync)

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if *collection_name* exists.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """
        client = self._get_client()

        def _sync() -> bool:
            try:
                client.get_collection(collection_name)
                return True
            except Exception:
                return False

        return await asyncio.to_thread(_sync)

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return collection metadata (``{}`` if absent).

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> dict:
            try:
                col = client.get_collection(collection_name)
                return col.metadata or {}
            except Exception:
                return {}

        return await asyncio.to_thread(_sync)

    def reset_for_testing(self) -> None:
        """Reset the cached client.  **For use in tests only.**

        :return: (None) This method does not return a value.
        """
        self._client = None
````

## File: src/mcp_project_context_server/integrations/vectorstore/chroma_local/client.py
````python
"""ChromaDB local (persistent) vector store provider.

Configuration
-------------
``CHROMA_DIR``
    Directory where ChromaDB stores its database files.
    Defaults to ``~/.mcp-data/chroma``.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Optional

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)

logger = logging.getLogger(__name__)

_DEFAULT_DIR: Path = Path.home() / ".mcp-data" / "chroma"


class ChromaLocalVectorStoreProvider:
    """Vector store backed by a local ChromaDB PersistentClient.

    Initialization is deferred: the ChromaDB client and directory are created
    on the first method call, not at import time.
    """

    def __init__(self) -> None:
        """Initialize the provider, reading ``CHROMA_DIR`` from the environment."""
        self._dir: Path = Path(os.getenv("CHROMA_DIR", str(_DEFAULT_DIR))).expanduser()
        self._client: Optional[Any] = None

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "chroma-local"

    def _get_client(self) -> Any:
        """Return the ChromaDB client, initialising on first call."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings

            self._dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(self._dir),
                settings=Settings(anonymized_telemetry=False),
            )
        return self._client

    # ------------------------------------------------------------------
    # VectorStoreProvider Protocol implementation
    # ------------------------------------------------------------------

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Drop and recreate *name* for a clean re-index (ADR-00006).

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                client.delete_collection(name)
            except Exception:
                pass
            client.create_collection(name=name, metadata=metadata or {})

        await asyncio.to_thread(_sync)

    async def delete_collection(self, name: str) -> None:
        """Delete *name*, silently succeeding if it does not exist.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                client.delete_collection(name)
            except Exception:
                pass

        await asyncio.to_thread(_sync)

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Add or update documents in *collection_name*.

        :param collection_name: (str) Target collection.
        :param ids: (list) Per-document unique identifiers.
        :param embeddings: (list) Per-document embedding vectors (must all be the same length).
        :param documents: (list) Raw text for each document.
        :param metadatas: (list) Per-document metadata dicts.
        :return: (None) This method does not return a value.
        :raises VectorStoreError: If the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> None:
            try:
                col = client.get_collection(collection_name)
            except Exception as exc:
                raise VectorStoreError(f"Collection '{collection_name}' not found: {exc}") from exc
            col.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

        await asyncio.to_thread(_sync)

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run a nearest-neighbour search.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> QueryResult:
            try:
                col = client.get_collection(collection_name)
            except Exception as exc:
                raise VectorStoreError(f"Collection '{collection_name}' not found: {exc}") from exc
            n = min(n_results, col.count())
            if n == 0:
                return QueryResult(ids=[], documents=[], metadatas=[], distances=[])
            raw = col.query(query_embeddings=[query_embedding], n_results=n)
            return QueryResult(
                ids=raw["ids"][0] if raw.get("ids") else [],
                documents=raw["documents"][0] if raw.get("documents") else [],
                metadatas=raw["metadatas"][0] if raw.get("metadatas") else [],
                distances=raw["distances"][0] if raw.get("distances") else [],
            )

        return await asyncio.to_thread(_sync)

    async def count(self, collection_name: str) -> int:
        """Return the document count for *collection_name* (0 if absent).

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> int:
            try:
                return client.get_collection(collection_name).count()
            except Exception:
                return 0

        return await asyncio.to_thread(_sync)

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if *collection_name* exists.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """
        client = self._get_client()

        def _sync() -> bool:
            try:
                client.get_collection(collection_name)
                return True
            except Exception:
                return False

        return await asyncio.to_thread(_sync)

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return metadata attached to *collection_name* (``{}`` if absent).

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection does not exist.
        """
        client = self._get_client()

        def _sync() -> dict:
            try:
                col = client.get_collection(collection_name)
                return col.metadata or {}
            except Exception:
                return {}

        return await asyncio.to_thread(_sync)

    def reset_for_testing(self) -> None:
        """Reset the cached client.  **For use in tests only.**

        :return: (None) This method does not return a value.
        """
        self._client = None
````

## File: src/mcp_project_context_server/integrations/vectorstore/pgvector/client.py
````python
"""PostgreSQL + pgvector vector store provider.

Configuration
-------------
``PGVECTOR_CONNECTION_STRING``
    A libpq-compatible connection string, e.g.:
    ``postgresql://{user}:{password}@{host}:5432/dbname``

Design
------
* One table per collection: ``vs_<sanitised_collection_name>``
* A ``vs_collections`` sidecar table stores collection metadata and the
  embedding dimension (derived from the first upsert call).
* Vectors are stored as ``vector(N)`` using the pgvector extension.
* The drop-and-recreate indexing strategy (ADR-00006) is implemented by
  ``create_collection`` — it drops the table and recreates it.
"""
import logging
import os
import re
from typing import Any, Optional

from mcp_project_context_server.integrations.vectorstore.base import (
    QueryResult,
    VectorStoreError,
)

logger = logging.getLogger(__name__)

_TABLE_PREFIX = "vs_"


def _table_name(collection_name: str) -> str:
    """Sanitise *collection_name* into a safe PostgreSQL table name."""
    safe = re.sub(r"[^a-z0-9_]", "_", collection_name.lower())
    return f"{_TABLE_PREFIX}{safe}"


class PgVectorStoreProvider:
    """Vector store backed by PostgreSQL with the pgvector extension.

    Uses ``asyncpg`` for async PostgreSQL access.  The pgvector extension
    must already be installed in the target database::

        CREATE EXTENSION IF NOT EXISTS vector;
    """

    def __init__(self) -> None:
        """Initialize the provider, reading ``PGVECTOR_CONNECTION_STRING`` from the environment.

        :raises EnvironmentError: If ``PGVECTOR_CONNECTION_STRING`` is not set.
        """
        self._dsn: Optional[str] = os.getenv("PGVECTOR_CONNECTION_STRING")
        if not self._dsn:
            raise EnvironmentError(
                "PGVECTOR_CONNECTION_STRING environment variable is required " "when VECTOR_STORE_PROVIDER=pgvector"
            )
        self._pool: Optional[Any] = None

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "pgvector"

    async def _get_pool(self) -> Any:
        """Return the asyncpg connection pool, creating it on first call."""
        if self._pool is None:
            try:
                import asyncpg  # type: ignore[import]
            except ImportError as exc:
                raise ImportError(
                    "asyncpg is required for pgvector support.  "
                    "Install it with: pip install mcp-project-context-server[pgvector]"
                ) from exc

            # Register the pgvector codec so asyncpg can decode vector columns
            async def _init(conn: Any) -> None:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")  # type: ignore[attr-defined]
                await conn.set_type_codec(  # type: ignore[attr-defined]
                    "vector",
                    encoder=lambda v: str(v),
                    decoder=lambda v: [float(x) for x in v.strip("[]").split(",")],
                    schema="public",
                    format="text",
                )

            self._pool = await asyncpg.create_pool(self._dsn, init=_init)  # type: ignore[attr-defined]

            # Ensure sidecar table exists
            async with self._pool.acquire() as conn:  # type: ignore[attr-defined]
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS vs_collections (
                        name        TEXT PRIMARY KEY,
                        dimension   INT,
                        metadata    JSONB DEFAULT '{}'
                    )
                """)

        return self._pool

    # ------------------------------------------------------------------
    # VectorStoreProvider Protocol implementation
    # ------------------------------------------------------------------

    async def create_collection(self, name: str, metadata: dict | None = None) -> None:
        """Drop and recreate the table for *name* (ADR-00006).

        Dimension is not known at creation time — the vector column is added
        on the first ``upsert`` call once the dimension is established.

        :param name: (str) Collection name.
        :param metadata: (dict) Optional key/value metadata to attach to the collection.
        :return: (None) This method does not return a value.
        """
        pool = await self._get_pool()
        tbl = _table_name(name)
        import json

        async with pool.acquire() as conn:  # type: ignore[attr-defined]
            await conn.execute(f"DROP TABLE IF EXISTS {tbl}")
            await conn.execute("DELETE FROM vs_collections WHERE name = $1", name)
            await conn.execute(
                "INSERT INTO vs_collections (name, dimension, metadata) VALUES ($1, NULL, $2::jsonb)",
                name,
                json.dumps(metadata or {}),
            )

    async def delete_collection(self, name: str) -> None:
        """Drop the table for *name* and remove from sidecar.

        :param name: (str) Collection name.
        :return: (None) This method does not return a value.
        """
        try:
            pool = await self._get_pool()
            tbl = _table_name(name)
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                await conn.execute(f"DROP TABLE IF EXISTS {tbl}")
                await conn.execute("DELETE FROM vs_collections WHERE name = $1", name)
        except Exception:
            pass

    async def _ensure_table(self, conn: Any, name: str, dimension: int) -> None:
        """Create the vector table for *name* if it does not yet exist."""
        tbl = _table_name(name)
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {tbl} (
                id          TEXT PRIMARY KEY,
                embedding   vector({dimension}),
                document    TEXT,
                metadata    JSONB DEFAULT '{{}}'
            )
            """)  # type: ignore[attr-defined]
        await conn.execute(  # type: ignore[attr-defined]
            f"CREATE INDEX IF NOT EXISTS {tbl}_emb_idx ON {tbl} USING ivfflat (embedding vector_cosine_ops)"
        )
        await conn.execute(  # type: ignore[attr-defined]
            "UPDATE vs_collections SET dimension = $1 WHERE name = $2 AND dimension IS NULL",
            dimension,
            name,
        )

    async def upsert(
        self,
        collection_name: str,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Insert or update documents in *collection_name*.

        :param collection_name: (str) Target collection.
        :param ids: (list) Per-document unique identifiers.
        :param embeddings: (list) Per-document embedding vectors (must all be the same length).
        :param documents: (list) Raw text for each document.
        :param metadatas: (list) Per-document metadata dicts.
        :return: (None) This method does not return a value.
        """
        if not ids:
            return
        import json

        dimension = len(embeddings[0])
        pool = await self._get_pool()
        tbl = _table_name(collection_name)

        async with pool.acquire() as conn:  # type: ignore[attr-defined]
            await self._ensure_table(conn, collection_name, dimension)
            for doc_id, emb, doc, meta in zip(ids, embeddings, documents, metadatas):
                vec_str = "[" + ",".join(str(v) for v in emb) + "]"
                await conn.execute(  # type: ignore[attr-defined]
                    f"""
                    INSERT INTO {tbl} (id, embedding, document, metadata)
                    VALUES ($1, $2::vector, $3, $4::jsonb)
                    ON CONFLICT (id) DO UPDATE
                        SET embedding = EXCLUDED.embedding,
                            document  = EXCLUDED.document,
                            metadata  = EXCLUDED.metadata
                    """,
                    doc_id,
                    vec_str,
                    doc,
                    json.dumps(meta),
                )

    async def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> QueryResult:
        """Run cosine-similarity nearest-neighbour search.

        :param collection_name: (str) Collection to search.
        :param query_embedding: (list) Query vector (must match the dimension of stored embeddings).
        :param n_results: (int) Maximum number of results to return.
        :return: (QueryResult) A :class:`QueryResult` with the top-*n_results* matches.
        :raises VectorStoreError: If the query fails.
        """
        import json

        pool = await self._get_pool()
        tbl = _table_name(collection_name)
        vec_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

        try:
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                rows = await conn.fetch(  # type: ignore[attr-defined]
                    f"""
                    SELECT id, document, metadata,
                           1 - (embedding <=> $1::vector) AS similarity
                    FROM {tbl}
                    ORDER BY embedding <=> $1::vector
                    LIMIT $2
                    """,
                    vec_str,
                    n_results,
                )
        except Exception as exc:
            raise VectorStoreError(f"Query failed on collection '{collection_name}': {exc}") from exc

        return QueryResult(
            ids=[r["id"] for r in rows],
            documents=[r["document"] for r in rows],
            metadatas=[json.loads(r["metadata"]) for r in rows],
            distances=[float(r["similarity"]) for r in rows],
        )

    async def count(self, collection_name: str) -> int:
        """Return document count (0 if table absent).

        :param collection_name: (str) Collection to count.
        :return: (int) Document count. Returns 0 if the collection does not exist.
        """
        try:
            pool = await self._get_pool()
            tbl = _table_name(collection_name)
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                row = await conn.fetchrow(f"SELECT COUNT(*) AS n FROM {tbl}")  # type: ignore[attr-defined]
                return int(row["n"])
        except Exception:
            return 0

    async def collection_exists(self, collection_name: str) -> bool:
        """Return ``True`` if a row exists in the sidecar for *collection_name*.

        :param collection_name: (str) Collection to check.
        :return: (bool) ``True`` if the collection exists, ``False`` otherwise.
        """
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                row = await conn.fetchrow(  # type: ignore[attr-defined]
                    "SELECT 1 FROM vs_collections WHERE name = $1", collection_name
                )
                return row is not None
        except Exception:
            return False

    async def get_collection_metadata(self, collection_name: str) -> dict:
        """Return metadata from the sidecar (``{}`` if absent).

        :param collection_name: (str) Collection to inspect.
        :return: (dict) Metadata dict (may be empty). Returns ``{}`` if the collection does not exist.
        """
        try:
            import json

            pool = await self._get_pool()
            async with pool.acquire() as conn:  # type: ignore[attr-defined]
                row = await conn.fetchrow(  # type: ignore[attr-defined]
                    "SELECT metadata FROM vs_collections WHERE name = $1", collection_name
                )
                if row is None:
                    return {}
                return json.loads(row["metadata"]) if row["metadata"] else {}
        except Exception:
            return {}

    async def close(self) -> None:
        """Close the connection pool.  Call on server shutdown.

        :return: (None) This method does not return a value.
        """
        if self._pool is not None:
            await self._pool.close()  # type: ignore[attr-defined]
            self._pool = None

    def reset_for_testing(self) -> None:
        """Reset the cached pool.  **For use in tests only.**

        :return: (None) This method does not return a value.
        """
        self._pool = None
````

## File: src/mcp_project_context_server/integrations/vectorstore/registry.py
````python
"""Vector store provider registry — factory driven by ``VECTOR_STORE_PROVIDER`` env var.

Design rules
------------
* ``chroma-local`` is the **default** when ``VECTOR_STORE_PROVIDER`` is not set.
  This preserves backward compatibility for local developer setups.
* Unknown values raise ``EnvironmentError`` immediately at startup (fail-fast).
* The provider singleton is cached after the first call.

Supported ``VECTOR_STORE_PROVIDER`` values
------------------------------------------
``chroma-local`` *(default)*
    Local ChromaDB PersistentClient.  Requires ``CHROMA_DIR`` (optional,
    defaults to ``~/.mcp-data/chroma``).

``chroma-http``
    Remote ChromaDB HTTP server.  Requires ``CHROMA_HOST``, ``CHROMA_PORT``
    (optional, defaults to ``localhost:8000``).  Optional: ``CHROMA_API_KEY``.

``pgvector``
    PostgreSQL with the pgvector extension.  Requires
    ``PGVECTOR_CONNECTION_STRING``.

``gcp-vector-search``
    Google Cloud Vertex AI Vector Search against a pre-provisioned Index and
    IndexEndpoint (ADR-00023; this provider does not create or deploy GCP
    infrastructure).  Requires ``GCP_VECTOR_SEARCH_PROJECT``,
    ``GCP_VECTOR_SEARCH_LOCATION``, ``GCP_VECTOR_SEARCH_INDEX_ID``,
    ``GCP_VECTOR_SEARCH_INDEX_ENDPOINT_ID``, and
    ``GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID``.  Optional:
    ``GCP_VECTOR_SEARCH_FIRESTORE_COLLECTION``.

Incompatible combinations
-------------------------
``EMBED_PROVIDER=vertexai`` cannot be combined with ``chroma-local`` or
``chroma-http``: the two SDKs deadlock when loaded into the same process on
Windows.  Use ``VECTOR_STORE_PROVIDER=pgvector`` with Vertex AI instead.
"""
import logging
import os
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

from mcp_project_context_server.indexing.indexer import run_index_pipeline
from mcp_project_context_server.integrations.vectorstore.base import VectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.chroma_http.client import ChromaHttpVectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.chroma_local.client import ChromaLocalVectorStoreProvider
from mcp_project_context_server.integrations.vectorstore.gcp_vector_search.client import GcpVectorSearchProvider
from mcp_project_context_server.integrations.vectorstore.pgvector.client import PgVectorStoreProvider

logger = logging.getLogger(__name__)

_SUPPORTED_PROVIDERS: frozenset[str] = frozenset({"chroma-local", "chroma-http", "pgvector", "gcp-vector-search"})
_DEFAULT_PROVIDER: str = "chroma-local"

# EMBED_PROVIDER values that cannot share a process with the given
# VECTOR_STORE_PROVIDER.  The vertexai SDK and the chromadb client (both of
# which pull in native/C-extension dependencies) deadlock when imported into
# the same Windows process -- this is an in-process native-library conflict,
# not a credentials or network issue, so it cannot be worked around by
# retrying or adding timeouts.
INCOMPATIBLE_EMBED_PROVIDERS_BY_VECTOR_STORE: dict[str, frozenset[str]] = {
    "chroma-local": frozenset({"vertexai"}),
    "chroma-http": frozenset({"vertexai"}),
}

IndexFn = Callable[[str | Path], Coroutine[Any, Any, str]]


def _assert_compatible_providers(vector_store_provider_name: str) -> None:
    """Raise if the configured EMBED_PROVIDER cannot be used with *vector_store_provider_name*."""
    embed_provider_name = os.getenv("EMBED_PROVIDER", "").strip().lower()
    incompatible = INCOMPATIBLE_EMBED_PROVIDERS_BY_VECTOR_STORE.get(vector_store_provider_name, frozenset())
    if embed_provider_name in incompatible:
        raise EnvironmentError(
            f"EMBED_PROVIDER='{embed_provider_name}' cannot be used with "
            f"VECTOR_STORE_PROVIDER='{vector_store_provider_name}': these two SDKs "
            "deadlock when loaded into the same process on Windows.  Use "
            "VECTOR_STORE_PROVIDER=pgvector with EMBED_PROVIDER=vertexai instead."
        )


def get_vector_store() -> VectorStoreProvider:
    """Return the configured vector store provider singleton.

    :return: (VectorStoreProvider) The vector store provider instance selected by
        ``VECTOR_STORE_PROVIDER`` (defaults to ``"chroma-local"``).
    :raises EnvironmentError: If ``VECTOR_STORE_PROVIDER`` is set to an unrecognised value,
        if the selected provider is missing a required env var, or if the
        configured ``EMBED_PROVIDER`` is incompatible with it.
    :raises ImportError: If the required package for the selected provider is not installed.
    """
    provider_name = os.getenv("VECTOR_STORE_PROVIDER", _DEFAULT_PROVIDER).strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported VECTOR_STORE_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    _assert_compatible_providers(provider_name)

    return _build_provider(provider_name)


def _build_provider(provider_name: str) -> VectorStoreProvider:
    """Instantiate and return the provider for *provider_name*."""
    if provider_name == "chroma-local":
        from mcp_project_context_server.integrations.vectorstore.chroma_local.client import (
            ChromaLocalVectorStoreProvider,
        )

        return ChromaLocalVectorStoreProvider()

    if provider_name == "chroma-http":
        from mcp_project_context_server.integrations.vectorstore.chroma_http.client import (
            ChromaHttpVectorStoreProvider,
        )

        return ChromaHttpVectorStoreProvider()

    if provider_name == "pgvector":
        from mcp_project_context_server.integrations.vectorstore.pgvector.client import (
            PgVectorStoreProvider,
        )

        return PgVectorStoreProvider()

    if provider_name == "gcp-vector-search":
        from mcp_project_context_server.integrations.vectorstore.gcp_vector_search.client import (
            GcpVectorSearchProvider,
        )

        return GcpVectorSearchProvider()

    raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover


def get_indexer() -> IndexFn:
    """Return the ``index_project_context`` callable for the configured provider.

    Each vector store provider owns its indexer in
    ``integrations/vectorstore/{provider}/indexer.py``.  This function resolves
    the correct one based on ``VECTOR_STORE_PROVIDER``, mirroring the dispatch
    logic of :func:`get_vector_store`.

    :return: (Callable) An async callable that indexes a project path and
        returns a human-readable summary string.
    :raises EnvironmentError: If ``VECTOR_STORE_PROVIDER`` is set to an unrecognised value,
        or if the configured ``EMBED_PROVIDER`` is incompatible with it.
    """
    provider_name = os.getenv("VECTOR_STORE_PROVIDER", _DEFAULT_PROVIDER).strip().lower()

    if provider_name not in _SUPPORTED_PROVIDERS:
        raise EnvironmentError(
            f"Unsupported VECTOR_STORE_PROVIDER value '{provider_name}'.  "
            f"Supported values are: {', '.join(sorted(_SUPPORTED_PROVIDERS))}"
        )

    _assert_compatible_providers(provider_name)

    if provider_name == "chroma-local":
        store = ChromaLocalVectorStoreProvider()
    elif provider_name == "chroma-http":
        store = ChromaHttpVectorStoreProvider()
    elif provider_name == "pgvector":
        store = PgVectorStoreProvider()
    elif provider_name == "gcp-vector-search":
        store = GcpVectorSearchProvider()
    else:
        raise EnvironmentError(f"Internal error: unhandled provider '{provider_name}'")  # pragma: no cover

    async def index_project_context(project_path: str | Path) -> str:
        """Run the indexing pipeline against a local ChromaDB PersistentClient.

        :param project_path: (str) Path to the project root or any file within it.
        :return: (str) A human-readable summary string describing what was indexed.
        """

        return await run_index_pipeline(project_path, store)

    return index_project_context
````

## File: src/mcp_project_context_server/tools/__init__.py
````python
"""MCP tool implementations package."""
````

## File: src/mcp_project_context_server/tools/list_repositories.py
````python
"""Tool: list_repositories — list accessible repositories via the configured provider."""
import logging

from mcp import types
from mcp.types import CallToolResult, TextContent

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import (
    get_repository_provider,
    validate_repo_access,
)

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> CallToolResult:
    """Handle the ``list_repositories`` tool call.

    :param arguments: (dict) Tool input dict. Optional key ``"org"`` filters by
        organisation/group name.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item.
    """
    org = arguments.get("org")
    try:
        provider = get_repository_provider()
        repos = await provider.list_repositories(org=org)
    except Exception as exc:
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Error listing repositories: {exc}")])

    # Only surface repositories the allowlist actually permits — in
    # multi-tenant mode the provider may still be able to see repos outside
    # APPROVED_ORGS/APPROVED_REPOS (e.g. via a broadly-scoped API token).
    allowed_repos = []
    for r in repos:
        try:
            validate_repo_access(r.identifier)
        except RepositoryError:
            continue
        allowed_repos.append(r)
    repos = allowed_repos

    if not repos:
        return types.CallToolResult(content=[types.TextContent(type="text", text="No repositories found.")])
    repos_structured_results = {}
    repos_content_results = []
    for r in repos:
        status = "indexed" if r.indexed else "not indexed"
        last_indexed = f" (last indexed: {r.last_indexed})" if r.last_indexed else ""
        repos_content_results.append(types.TextContent(type="text", text=f"- **{r.identifier}** — {r.description or 'no description'} [{status}{last_indexed}]"))
        repos_structured_results[r.identifier] = {
            "identifier": types.TextContent(type="text", text=r.identifier),
            "description": types.TextContent(type="text", text=r.description or 'no description'),
            "status": types.TextContent(type="text", text=status),
            "last_indexed": types.TextContent(type="text", text=last_indexed),
        }
    return types.CallToolResult(content=repos_content_results, structuredContent=repos_structured_results)
````

## File: src/mcp_project_context_server/tools/search_shared.py
````python
"""Shared semantic-search implementation used by the `search_*_index`/`search_session_files` tools.

Before executing a search, the tool reads the provenance metadata stored on
the collection at index time and compares it against the current provider
configuration.  If the embedding provider or model has changed, a warning is
prepended to the results so the user knows the index may need rebuilding.
"""
import logging
import os

from mcp import types

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

from mcp_project_context_server.exceptions import EmbeddingError
from mcp_project_context_server.helpers.context import (
    collection_name_for,
    collection_name_for_repo_id,
    find_context_dir,
    resolve_project_path,
)
from mcp_project_context_server.integrations.embeddings.registry import get_embedding_provider
from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import get_repository_provider, validate_repo_access
from mcp_project_context_server.integrations.vectorstore.base import VectorStoreError
from mcp_project_context_server.integrations.vectorstore.registry import get_vector_store

logger = logging.getLogger(__name__)

_MISMATCH_WARNING = (
    "⚠️  **Provider mismatch detected** — the index was built with "
    "`{old_provider}/{old_model}` but the current provider is "
    "`{new_provider}/{new_model}`.  Search results may be inaccurate.  "
    "Please re-run `index_project_context` to rebuild the index."
)

_VERSION_MISMATCH_WARNING = (
    "⚠️  **Server version mismatch detected** — the index was built with "
    "server version `{old_version}` but the running server is "
    "`{new_version}`.  Please re-run `index_project_context` to rebuild the index."
)

# Floor applied to the over-fetch multiplier so a small `n_results` still
# pulls in enough candidates for the client-side prefix filter to find hits.
_OVER_FETCH_FLOOR = 25
_OVER_FETCH_MULTIPLIER = 5


def _empty_result(text: str) -> types.CallToolResult:
    """Build a `CallToolResult` for an early-return/error path with no hits."""
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text)],
        structured_content={"results": []},
    )


async def run_search(
    project_path: str, query: str, n_results: int, file_prefix: str | None = None
) -> types.CallToolResult:
    """Run a semantic search over the indexed `.context/` collection.

    :param project_path: (str) The project root, short repo identifier, or repository URL.
    :param query: (str) The natural-language search query.
    :param n_results: (int) The number of results to return to the caller.
    :param file_prefix: (str) When set, only hits whose ``metadata["file"]`` starts
        with this prefix are returned (used to scope search to ``decisions/`` or
        ``sessions/``). The store is over-fetched so the filter still has enough
        candidates to select from.
    :return: (CallToolResult) The unstructured text (matching context snippets,
        optionally prefixed with a provider/model mismatch warning, or an
        error/"not found" message) alongside a ``structured_content`` object of
        the shape ``{"results": [{"file", "chunk", "content", "distance"}, ...]}``.
    """
    try:
        validate_repo_access(project_path)
    except RepositoryError as exc:
        return _empty_result(str(exc))

    repo_provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(project_path, repo_provider.provider_name)

    if is_remote:
        col_name = collection_name_for_repo_id(resolved_path)
    else:
        context_dir = find_context_dir(resolved_path)
        if not context_dir:
            return _empty_result(f"No .context/ directory found near {project_path}")
        col_name = collection_name_for(context_dir)

    store = get_vector_store()

    if not await store.collection_exists(col_name):
        return _empty_result(f"Collection '{col_name}' not found. Run index_project_context first.")

    # --- Provenance mismatch check ---
    warnings: list[str] = []
    stored_meta = await store.get_collection_metadata(col_name)
    current_provider = get_embedding_provider()
    stored_embed_provider = stored_meta.get("embed_provider", "")
    stored_embed_model = stored_meta.get("embed_model", "")

    if stored_embed_provider and stored_embed_model:
        if stored_embed_provider != current_provider.provider_name or stored_embed_model != current_provider.model_name:
            warnings.append(
                _MISMATCH_WARNING.format(
                    old_provider=stored_embed_provider,
                    old_model=stored_embed_model,
                    new_provider=current_provider.provider_name,
                    new_model=current_provider.model_name,
                )
            )

    stored_server_version = stored_meta.get("server_version", "")
    if stored_server_version and stored_server_version != __version__:
        warnings.append(
            _VERSION_MISMATCH_WARNING.format(
                old_version=stored_server_version,
                new_version=__version__,
            )
        )

    warning_prefix = "\n\n".join(warnings) + "\n\n---\n\n" if warnings else ""

    query_n_results = n_results
    if file_prefix is not None:
        query_n_results = max(n_results * _OVER_FETCH_MULTIPLIER, _OVER_FETCH_FLOOR)

    try:
        provider = get_embedding_provider()
        query_embedding = await provider.embed_chunk(query)
        result = await store.query(
            collection_name=col_name,
            query_embedding=query_embedding,
            n_results=query_n_results,
        )
    except (VectorStoreError, EmbeddingError) as exc:
        return _empty_result(f"Search failed: {exc}")

    documents = result.documents
    metadatas = result.metadatas
    distances = result.distances if len(result.distances) == len(documents) else [None] * len(documents)

    if file_prefix is not None:
        filtered = [
            (doc, meta, dist)
            for doc, meta, dist in zip(documents, metadatas, distances)
            if meta.get("file", "").startswith(file_prefix)
        ]
        filtered = filtered[:n_results]
        documents = [doc for doc, _, _ in filtered]
        metadatas = [meta for _, meta, _ in filtered]
        distances = [dist for _, _, dist in filtered]

    if not documents:
        return _empty_result(f"{warning_prefix}No results found.")

    items = [
        {"file": meta.get("file", "?"), "chunk": meta.get("chunk"), "content": doc, "distance": dist}
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]
    output_parts = [f"**[{item['file']}]**\n{item['content']}" for item in items]
    body = "\n\n---\n\n".join(output_parts)

    structured_content: dict = {"results": items}
    if warning_prefix:
        structured_content["warning"] = warning_prefix.strip()

    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f"{warning_prefix}{body}")],
        structured_content=structured_content,
    )
````

## File: src/mcp_project_context_server/transport/sse.py
````python
"""HTTP/SSE transport — general-purpose MCP over HTTP with pluggable authentication.

This transport is not tied to any specific LLM platform.  It can be used with any
MCP client that supports the HTTP/SSE protocol, including Gemini Enterprise Agent
Engine, remote Cursor deployments, and self-hosted team servers.

Configuration
-------------
``MCP_HOST``
    Bind address.  Defaults to ``0.0.0.0``.

``MCP_PORT``
    Listen port.  Defaults to ``8080``.

``MCP_AUTH_TYPE``
    Authentication type.  One of:

    ``none``
        No authentication.  Suitable for trusted internal networks.

    ``bearer``
        Static API key via ``Authorization: Bearer <token>`` header.
        Requires ``MCP_AUTH_TOKEN``.

    ``google-iam``
        Google Cloud identity token validated via ``google-auth``.
        Suitable for Gemini Enterprise Agent Engine deployments.
        Optional: ``GOOGLE_IAM_AUDIENCE``, ``GOOGLE_SERVICE_ACCOUNT_KEY_PATH``,
        ``GOOGLE_APPROVED_SERVICE_ACCOUNTS``.

``MCP_AUTH_TOKEN``
    Required when ``MCP_AUTH_TYPE=bearer``.

``GOOGLE_IAM_AUDIENCE``
    Expected ``aud`` claim in Google identity tokens.  If unset, audience
    validation is skipped (less secure — set this in production).

``GOOGLE_SERVICE_ACCOUNT_KEY_PATH``
    Path to a service account JSON key file.  If unset, Application Default
    Credentials (ADC) are used instead.

``GOOGLE_APPROVED_SERVICE_ACCOUNTS``
    Comma-separated list of allowed caller service account emails.
    If unset, any authenticated Google identity is accepted.
"""

import logging
import os
from collections.abc import Callable
from typing import Any

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

logger = logging.getLogger(__name__)

_DEFAULT_HOST = "0.0.0.0"
_DEFAULT_PORT = 8080


# ---------------------------------------------------------------------------
# Auth middleware implementations
# ---------------------------------------------------------------------------


class _BearerAuthMiddleware(BaseHTTPMiddleware):
    """Validate ``Authorization: Bearer <token>`` against a static token."""

    def __init__(self, app: Any, token: str) -> None:
        super().__init__(app)
        self._token = token

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Health-check endpoint is unauthenticated
        if request.url.path == "/health":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "Missing or invalid Authorization header"}, status_code=401)
        token = auth_header.removeprefix("Bearer ").strip()
        if token != self._token:
            return JSONResponse({"error": "Invalid bearer token"}, status_code=403)
        return await call_next(request)


class _GoogleIAMAuthMiddleware(BaseHTTPMiddleware):
    """Validate Google Cloud identity tokens (for Agent Engine and service-to-service auth)."""

    def __init__(
        self,
        app: Any,
        audience: str | None,
        approved_accounts: frozenset[str] | None,
    ) -> None:
        super().__init__(app)
        self._audience = audience
        self._approved_accounts = approved_accounts

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path == "/health":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "Missing Authorization header"}, status_code=401)

        id_token = auth_header.removeprefix("Bearer ").strip()

        try:
            import asyncio

            claims = await asyncio.to_thread(self._verify_token, id_token)
        except Exception as exc:
            logger.warning("Google IAM token verification failed: %s", exc)
            return JSONResponse({"error": f"Token verification failed: {exc}"}, status_code=403)

        if self._approved_accounts:
            email = claims.get("email", "")
            if email not in self._approved_accounts:
                logger.warning("Rejected Google identity: %s (not in approved list)", email)
                return JSONResponse({"error": "Service account not approved"}, status_code=403)

        return await call_next(request)

    def _verify_token(self, id_token: str) -> dict:
        """Verify *id_token* synchronously (called via asyncio.to_thread)."""
        try:
            from google.auth.transport import requests as google_requests  # type: ignore[import]
            from google.oauth2 import id_token as google_id_token  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "google-auth is required for google-iam auth.  "
                "Install it with: pip install mcp-project-context-server[sse]"
            ) from exc

        request = google_requests.Request()
        claims = google_id_token.verify_firebase_token(id_token, request, audience=self._audience)
        return dict(claims)


# ---------------------------------------------------------------------------
# Starlette app factory
# ---------------------------------------------------------------------------


def _build_auth_middleware(auth_type: str) -> list[Middleware]:
    """Build the Starlette middleware list for *auth_type*."""
    if auth_type == "none":
        return []

    if auth_type == "bearer":
        token = os.getenv("MCP_AUTH_TOKEN", "")
        if not token:
            raise EnvironmentError("MCP_AUTH_TOKEN must be set when MCP_AUTH_TYPE=bearer")
        return [Middleware(_BearerAuthMiddleware, token=token)]

    if auth_type == "google-iam":
        audience = os.getenv("GOOGLE_IAM_AUDIENCE") or None
        approved_raw = os.getenv("GOOGLE_APPROVED_SERVICE_ACCOUNTS", "")
        approved: frozenset[str] | None = frozenset(a.strip() for a in approved_raw.split(",") if a.strip()) or None
        return [Middleware(_GoogleIAMAuthMiddleware, audience=audience, approved_accounts=approved)]

    raise EnvironmentError(
        f"Unsupported MCP_AUTH_TYPE value '{auth_type}'.  " "Supported values are: none, bearer, google-iam"
    )


def build_sse_app(server: Server) -> Starlette:
    """Build and return the Starlette ASGI application for HTTP/SSE transport.

    :param server: (Server) The configured MCP :class:`Server` instance.
    :return: (Starlette) A :class:`~starlette.applications.Starlette` app ready
        to be served by uvicorn.
    :raises EnvironmentError: If auth configuration is invalid or incomplete.
    """
    auth_type = os.getenv("MCP_AUTH_TYPE", "none").strip().lower()
    middleware = _build_auth_middleware(auth_type)

    sse_transport = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())
        return Response()

    async def health(_: Request) -> Response:
        return JSONResponse({"status": "ok"})

    routes = [
        Route("/sse", endpoint=handle_sse),
        Route("/health", endpoint=health),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]

    return Starlette(routes=routes, middleware=middleware)


async def run_sse(server: Server) -> None:
    """Run *server* over HTTP/SSE until interrupted.

    Reads ``MCP_HOST`` and ``MCP_PORT`` from the environment.

    :param server: (Server) The configured MCP :class:`Server` instance.
    :return: (None) This function does not return a value.
    """
    import uvicorn  # type: ignore[import]

    host = os.getenv("MCP_HOST", _DEFAULT_HOST)
    port = int(os.getenv("MCP_PORT", str(_DEFAULT_PORT)))
    auth_type = os.getenv("MCP_AUTH_TYPE", "none").strip().lower()

    logger.info(
        "Starting MCP server in HTTP/SSE mode on %s:%d (auth: %s)",
        host,
        port,
        auth_type,
    )

    app = build_sse_app(server)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    uvicorn_server = uvicorn.Server(config)
    await uvicorn_server.serve()
````

## File: src/mcp_project_context_server/transport/stdio.py
````python
"""STDIO transport — the default MCP transport for local tool clients.

No configuration required.  The server reads from stdin and writes to stdout,
which is how Claude Desktop, Claude Code, Cursor, JetBrains AI Assistant,
Continue Dev, and GitHub Copilot all launch MCP servers locally.
"""

import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server

logger = logging.getLogger(__name__)


async def run_stdio(server: Server) -> None:
    """Run *server* over STDIO until the stream is closed.

    :param server: (Server) The configured MCP :class:`Server` instance.
    :return: (None) This function does not return a value.
    """
    logger.info("Starting MCP server in STDIO mode")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
````

## File: scripts/test_client.py
````python
# test_client.py
import asyncio
import os
from pathlib import Path
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# Resolve the src/ directory so the package is importable by the subprocess
SRC_DIR = str(Path(__file__).parent.parent / "src")

async def test():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_project_context_server"],
        env={**os.environ, "PYTHONPATH": SRC_DIR},
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Available tools: {tools}")

asyncio.run(test())
````

## File: src/mcp_project_context_server/__init__.py
````python
"""mcp-project-context-server — MCP server for persistent project context."""

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"
````

## File: src/mcp_project_context_server/__main__.py
````python
"""Entry point for running the server as a module (``python -m mcp_project_context_server``)."""
import argparse

from mcp_project_context_server.helpers.logs import ParseLogLevel, setup_logging
from mcp_project_context_server.server import run

parser = argparse.ArgumentParser()
parser.add_argument(
    "--log-level",
    action=ParseLogLevel,
    metavar="name=LEVEL",
    dest="log_level",
    default={},
    help="Override log level for a specific logger, e.g. urllib3=WARNING. "
         "Can be passed multiple times.",
)

arguments = parser.parse_args()
setup_logging(arguments.log_level)
run()
````

## File: .coveragerc.toml
````toml
[run]
# Source directory for coverage measurement
source = ["src"]

# Disable C-extension tracing to prevent segfaults with chromadb on Python 3.11
# See: https://github.com/chroma-core/chroma/issues — chromadb C extensions conflict
# with coverage's should_trace callback during collection.
concurrency = ["thread"]

# Files and directories to exclude from coverage measurement
omit = [
    # Tests directory
    "*/tests/*",
    # Python cache
    "*/__pycache__/*",
    # Third-party packages
    "*/site-packages/*",
    # Development tools
    "*/venv/*",
    "*/.venv/*",
    ".tox",
    "*/.tox/*",
    # IDE and editor files
    "*/.idea/*",
    "*/.vscode/*",
    # Docker related
    "*/Dockerfile",
    "*/docker-compose.yml",
    # Type stubs
    "*/.pyi",
    # Ignore coverage on specific lines
    "*/setup.py",
    "*/pyproject.toml",
    "*/scripts/*",
]

[report]
# Fail CI if coverage is below this threshold (optional)
# fail_under = 80

# Show missing lines (optional)
show_missing = true

[html]
# Directory to store HTML coverage report (optional)
directory = "htmlcov"

[xml]
# File name for XML coverage report for CI integration
report = "coverage.xml"

[yaml]
# Directory to store YAML coverage report (optional)
reportdir = "coverage_reduced"
````

## File: src/mcp_project_context_server/tools/index_context.py
````python
"""Tool: index_project_context — re-indexes .context/ into the configured vector store."""
import logging
import os

from mcp import types

from mcp_project_context_server.integrations.repository.base import RepositoryError
from mcp_project_context_server.integrations.repository.registry import validate_repo_access
from mcp_project_context_server.integrations.vectorstore.registry import get_indexer

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``index_project_context`` tool call.

    :param arguments: (dict) Tool input dict. Requires key ``"project_path"``.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        with the indexing result summary or an error message.
    """
    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    indexer = get_indexer()
    result = await indexer(_project_path)
    return [types.TextContent(type="text", text=result)]
````

## File: src/mcp_project_context_server/tools/save_session.py
````python
"""Tool: save_session_summary — writes a session summary to .context/sessions/."""
import logging
import os
from datetime import datetime

from mcp import types

from mcp_project_context_server.helpers.context import find_context_dir, resolve_project_path
from mcp_project_context_server.integrations.repository.base import RepositoryError, RepositoryProvider
from mcp_project_context_server.integrations.repository.registry import get_repository_provider, validate_repo_access

logger = logging.getLogger(__name__)


async def handle(arguments: dict) -> list[types.TextContent]:
    """Handle the ``save_session_summary`` tool call.

    :param arguments: (dict) Tool input dict. Requires keys ``"project_path"``
        and ``"summary"``.
    :return: (list) A list containing a single :class:`~mcp.types.TextContent` item
        confirming where the session summary was saved, or an error/"not found"
        message.
    """
    summary: str = arguments["summary"]

    _project_path = os.getenv("PROJECT_PATH", arguments["project_path"])
    try:
        validate_repo_access(_project_path)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=str(exc))]

    provider = get_repository_provider()
    resolved_path, is_remote = resolve_project_path(_project_path, provider.provider_name)

    if is_remote:
        return await _handle_remote(provider, resolved_path, summary)

    context_dir = find_context_dir(resolved_path)
    if not context_dir:
        return [
            types.TextContent(
                type="text",
                text=f"No .context/ directory found near {arguments['project_path']}",
            )
        ]

    sessions_dir = context_dir / "sessions"
    sessions_dir.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    session_file = sessions_dir / f"{today}.md"

    if session_file.exists():
        timestamp = datetime.now().strftime("%H:%M")
        file_content = f"{session_file.read_text(encoding='utf-8')}" f"\n\n### Session at {timestamp}\n\n{summary}"
    else:
        file_content = f"# Session: {today}\n\n{summary}"

    session_file.write_text(file_content, encoding="utf-8")
    # as_posix() gives a consistent forward-slash path regardless of platform.
    return [
        types.TextContent(
            type="text",
            text=f"Session summary saved to {session_file.as_posix()}",
        )
    ]


async def _handle_remote(provider: RepositoryProvider, repo_id: str, summary: str) -> list[types.TextContent]:
    """Save a session summary to a remote repository's ``.context/sessions/``.

    Write target is configurable via ``REPO_SESSION_WRITE_MODE``:

    * ``"direct"`` (default) — write straight to ``REPO_SESSION_BRANCH`` if
      set, otherwise the repository's default branch.
    * ``"branch"`` — create a new branch (``mcp-session/{date}-{HHMMSS}``)
      off the default branch and write there, leaving the target branch
      untouched for review.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    session_key = f"sessions/{today}.md"
    target_path = f".context/{session_key}"

    try:
        files = await provider.fetch_context_files(repo_id)
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=f"Error accessing repository: {exc}")]

    existing = files.get(session_key)
    if existing:
        timestamp = datetime.now().strftime("%H:%M")
        file_content = f"{existing}\n\n### Session at {timestamp}\n\n{summary}"
    else:
        file_content = f"# Session: {today}\n\n{summary}"

    message = f"Add session summary for {today}"
    write_mode = os.getenv("REPO_SESSION_WRITE_MODE", "direct").strip().lower()

    try:
        if write_mode == "branch":
            branch_name = f"mcp-session/{today}-{datetime.now().strftime('%H%M%S')}"
            await provider.create_branch(repo_id, branch_name)
            await provider.write_file(repo_id, target_path, file_content, message, branch=branch_name)
            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"Session summary pushed to new branch `{branch_name}` on `{repo_id}` "
                        f"(provider: {provider.provider_name}). Path: {target_path}"
                    ),
                )
            ]

        target_branch = os.getenv("REPO_SESSION_BRANCH") or None
        await provider.write_file(repo_id, target_path, file_content, message, branch=target_branch)
        branch_label = target_branch or await provider.get_default_branch(repo_id)
        return [
            types.TextContent(
                type="text",
                text=(
                    f"Session summary saved to `{repo_id}` ({target_path}) on branch "
                    f"`{branch_label}` (provider: {provider.provider_name})."
                ),
            )
        ]
    except RepositoryError as exc:
        return [types.TextContent(type="text", text=f"Error saving session summary: {exc}")]
````

## File: CHANGELOG.md
````markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.0.4] - 2026-04-17

### Fixed
- Refactor GitHub release creation in `build-and-publish.py` include a missing path to the location of the artifacts to be published. (`184d85e`)

---

## [0.0.3] - 2026-04-17

### Fixed
- Refactor GitHub release creation in `build-and-publish.py` to use `subprocess.Popen` for proper output capture; buffered output is now printed when the release process fails
- Improve error logging in `build-and-publish.py` so that buffered build output is printed when `python -m build` exits with a non-zero return code and `--verbose` is not set (`b423688`)

---

## [0.0.2] - 2026-04-17

### Fixed
- Improve error output in `build-and-publish.py` so that buffered build output is printed when the process exits with a non-zero return code and `--verbose` is not set (`b423688`)

---

## [0.0.1] - 2026-04-17

### Added
- Implement MCP project context server with semantic search via ChromaDB and Ollama embeddings (`41d1888`)
- Add `load_project_context`, `search_context`, `index_context`, and `save_session` MCP tools (`41d1888`)
- Add synchronous and asynchronous Ollama embedding client (`e1fbfc7`)
- Add heading-boundary chunking strategy for markdown indexing with intelligent sub-splitting (`a9f9d81`)
- Add Architecture Decision Records (ADRs) for server protocol, ChromaDB, and Ollama integration (`e5728d6`)
- Add ADR creation and review process documentation (`0bd33ed`)
- Add ADR-00010: GitHub Actions workflow for Codecov coverage uploads (`17713d4`)
- Add ADR-00012 and ADR-00013: targeted ADR/project tools and lightweight session initialization (`2f19a3e`)
- Add `build-and-publish.py` script for semantic versioning and automated GitHub releases (`e02dad0`)
- Add `build-and-publish.yml` GitHub Actions workflow for automated PyPI publishing on tag push (`e02dad0`)
- Add `codecov.yaml` GitHub Actions workflow for automated coverage uploads (`17713d4`)
- Add `.coveragerc.toml` with comprehensive coverage exclusion rules (`e420232`)
- Add `pytest.ini` to configure `pytest-asyncio` for asynchronous testing (`b00c6ca`)
- Add test suites: `test_helpers`, `test_tool_index_context`, `test_tool_load_context`, `test_tool_save_session`, `test_tool_search_context` (`3940347`)
- Add LICENSE (AGPLv3) and comprehensive README with setup instructions for all major MCP clients (`d80997b`, `312eae4`)
- Add README badges for PyPI version, downloads, coverage, last commit, and issues (`32a5c7c`, `6776ad5`)
- Add `CHROMA_DIR` environment variable documentation and server connection verification instructions to README (`60f4c4b`)
- Add dynamic version handling in `__init__.py` via `setuptools_scm` with `_version` fallback (`bd690e2`)
- Add `mypy` to test dependency group for static type checking (`b00c6ca`)

### Changed
- Refactor project namespace from `project_context_server` to `mcp_project_context_server` (`e1fbfc7`)
- Refactor project path handling to use `PROJECT_PATH` environment variable across all tools (`12d94ef`)
- Refactor test cases into class-based structures for improved organisation (`57522ef`)
- Refactor `search_context.py` to use `cast` for query embeddings and improve `None`-safety in result handling (`fc69c02`)
- Consolidate import statements and remove unnecessary whitespace across the codebase for consistency (`5faca4a`)
- Switch build backend from `hatchling` to `setuptools` with `setuptools_scm` for version management (`bd690e2`)
- Update project URLs in `pyproject.toml` to reflect `DarkMatterProductions` organisation branding (`47969a0`)
- Update `tag_regex` in `pyproject.toml` to correctly capture version numbers (`f60ef63`)
- Update CI to use `actions/checkout@v6` and `actions/setup-python@v6` (`3ee6cf2`)
- Update CI dependency installation to use `pip install testsuite` with explicit pip upgrade (`ee6c917`, `2e094b3`)
- Update `pyproject.toml` dependency versions for improved compatibility (`5faca4a`)

### Fixed
- Add specific `subprocess.CalledProcessError` handling in `build-and-publish.py` with detailed error output (`ed64a31`)
- Fix logging configuration in `server.py` to write to a log file instead of stderr (`bac831c`)

### Removed
- Remove legacy monolithic `context_server.py` and misplaced `AGENTS.md` references from project documentation (`caeda77`)
- Remove redundant `pip install -e .` step from CI configuration (`7f7983f`)
- Remove IntelliJ IDEA run configuration from version control (`d3893df`)

---

[Unreleased]: https://github.com/DarkMatterProductions/mcp-project-context-server/compare/cca6114...HEAD
````

## File: CLAUDE.md
````markdown
# Project Instructions

These instructions are for all agents working on this project. Please read them carefully and follow them closely. When in conflict, these rules supersede any other instructions. If you have any questions about these instructions, please ask for clarification.

- When working within this project, always leverage the tools provided by the `project_context` connector.
- At the start of every session, read and follow the instructions in the `.context/development-cycle.md` file.
- When generating an new ADR, always check if there is a `.context/adr-creation-and-review-process.md` file. If there is, follow the defined process for creating a new ADR.
- When reviewing an ADR, always check if there is a `.context/adr-creation-and-review-process.md` file. If there is, follow the defined process for reviewing and updating the ADR.
- When generating Commit Messages, always check if there is a `CONTRIBUTING.md` file. If there is, follow the guidelines in that file when generating the commit message.
- When generating Pull Request Descriptions, always check if there is a `CONTRIBUTING.md` file. If there is, follow the guidelines in that file when generating the pull request description.
- When generating Pull Request Titles, always check if there is a `CONTRIBUTING.md` file. If there is, follow the guidelines in that file when generating the pull request title.
````

## File: src/mcp_project_context_server/helpers/context.py
````python
"""Shared helpers for .context/ directory resolution and file reading."""
import logging
import re
from pathlib import Path

from mcp_project_context_server.integrations.repository.base import normalize_repo_identifier

logger = logging.getLogger(__name__)


def find_context_dir(project_path: str | Path) -> Path | None:
    """Walk up from project_path to find a .context/ directory.

    :param project_path: (str) The project root or subdirectory/file path to start searching from.
    :return: (Path) The first ``.context/`` directory found while walking up from
        ``project_path``, or ``None`` if none exists in any parent.
    """
    logger.debug(f"Executing 'find_context_dir' with the argument project_path: {project_path}")
    p = Path(project_path).resolve()
    for candidate in [p, *p.parents]:
        ctx = candidate / ".context"
        if ctx.is_dir():
            return ctx
    return None


def collection_name_for(context_dir: Path) -> str:
    """Derive a stable ChromaDB collection name from the project root.

    Always based on context_dir.parent so it is consistent regardless of
    whether the caller passed a project root, a subdirectory, or a file path.

    :param context_dir: (Path) The project's ``.context/`` directory.
    :return: (str) A sanitized, ChromaDB-safe collection name derived from the
        parent project directory's name, truncated to 63 characters.
    """
    project_name = context_dir.parent.name
    return f"ctx_{project_name}".replace("-", "_").replace(" ", "_")[:63]


def collection_name_for_repo_id(repo_id: str) -> str:
    """Derive a stable ChromaDB collection name from a remote repo identifier.

    Mirrors :func:`collection_name_for`'s sanitization, driven by the
    normalised ``owner/repo`` form so the same collection name is produced
    whether the caller passes a short identifier or a full URL.

    :param repo_id: (str) A short ``owner/repo`` identifier or a full remote repository URL.
    :return: (str) A sanitized, ChromaDB-safe collection name derived from the
        normalized repo identifier, truncated to 63 characters.
    """
    normalized = normalize_repo_identifier(repo_id)
    return f"ctx_{normalized}".replace("-", "_").replace(" ", "_").replace("/", "_")[:63]


def read_context_files(context_dir: Path) -> dict[str, str]:
    """Read all markdown files from .context/ into a dict.

    Keys use POSIX-style forward slashes (Path.as_posix()) so that ChromaDB
    document IDs and metadata are identical on Windows and Linux.

    :param context_dir: (Path) The project's ``.context/`` directory to read markdown files from.
    :return: (dict) A mapping of POSIX-style relative file paths to their markdown file contents.
    """
    return {
        md_file.relative_to(context_dir).as_posix(): md_file.read_text(encoding="utf-8")
        for md_file in context_dir.rglob("*.md")
    }


_SHORT_IDENTIFIER_RE = re.compile(r"^[\w.-]+/[\w.-]+$")


def resolve_project_path(raw: str, provider_name: str) -> tuple[str, bool]:
    """Resolve a raw project path string and determine whether it is remote.

    Remote resolution only applies when *provider_name* is not ``"local"``
    (i.e. ``REPO_PROVIDER`` has been explicitly set to a remote provider).
    When the provider is local, *raw* is always treated as a filesystem path,
    regardless of its shape. See ADR-00024.

    Returns a ``(resolved_path, is_remote)`` tuple.

    * If *provider_name* is ``"local"``: ``is_remote=False`` unconditionally.
    * If *raw* starts with ``http://`` or ``https://``: ``is_remote=True``.
    * If *raw* matches the ``owner/repo`` short identifier pattern
      (``^[\\w.-]+/[\\w.-]+$``): ``is_remote=True``.
    * Otherwise: ``is_remote=False`` (filesystem path — existing behaviour).

    :param raw: (str) The raw project path or identifier supplied by the caller.
    :param provider_name: (str) The active repository provider's name, from
        ``get_repository_provider().provider_name`` (i.e. ``REPO_PROVIDER``).
    :return: (tuple) A two-element tuple ``(resolved_path, is_remote)``.
    """
    logger.debug(f"Executing 'resolve_project_path' with raw: {raw}, provider_name: {provider_name}")
    if provider_name == "local":
        return raw, False
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw, True
    if _SHORT_IDENTIFIER_RE.match(raw):
        return raw, True
    return raw, False
````

## File: src/mcp_project_context_server/server.py
````python
"""MCP server setup, tool registry, and entry point.

Transport selection
-------------------
Set ``MCP_TRANSPORT`` to choose the transport:

``stdio`` *(default)*
    Standard input/output.  Used by Claude Desktop, Claude Code, Cursor,
    JetBrains AI Assistant, Continue Dev, and GitHub Copilot.

``sse``
    HTTP/SSE.  Used for remote deployments, team servers, and Gemini
    Enterprise Agent Engine.  See ``transport/sse.py`` for auth configuration.
"""

import asyncio
import logging
import os

from mcp.server import Server, ServerRequestContext
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    PaginatedRequestParams,
    TextContent,
    Tool,
)

from mcp_project_context_server.tools import (
    find_latest_session_file,
    index_context,
    list_repositories,
    load_context_files,
    reload_active_context_file,
    save_session,
    search_adr_index,
    search_context_index,
    search_session_files,
)

try:
    from mcp_project_context_server._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

logger = logging.getLogger(__name__)


_PROJECT_PATH_PROPERTY = {
    "type": "string",
    "description": (
        "Absolute filesystem path, a short 'owner/repo' identifier, " "or a full https:// repository URL."
    ),
}

_SEARCH_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "description": "Individual matching hits, one per matched chunk.",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": ".context/-relative path of the matched file."},
                    "chunk": {"type": ["integer", "null"], "description": "Chunk index within the file, if known."},
                    "content": {"type": "string", "description": "The matching chunk's text."},
                    "distance": {"type": ["number", "null"], "description": "Vector distance to the query, if known."},
                },
                "required": ["file", "content"],
            },
        },
        "warning": {
            "type": "string",
            "description": "Present only when the index was built with a different embedding provider/model.",
        },
    },
    "required": ["results"],
}

_TOOL_DEFINITIONS: list[Tool] = [
    Tool(
        name="search_context_index",
        description=(
            "Semantically search the whole indexed project context. "
            "Use this first to find which files are relevant to your task, then "
            "pass their paths to `load_context_files` — do not rely on this tool's "
            "snippets alone."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "query": {"type": "string", "description": "Natural language search query"},
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "query"],
        },
        output_schema=_SEARCH_OUTPUT_SCHEMA,
    ),
    Tool(
        name="search_adr_index",
        description=(
            "Semantically search only the architecture decision records under "
            ".context/decisions/. Use this to find ADRs relevant to your current "
            "task, then pass their paths to `load_context_files` — do not rely on this tool's "
            "snippets alone. If you need to search across all files in the project, use "
            "`search_project_files` instead."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "query": {"type": "string", "description": "Natural language search query"},
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "query"],
        },
        output_schema=_SEARCH_OUTPUT_SCHEMA,
    ),
    Tool(
        name="search_session_files",
        description=(
            "Semantically search only past session summaries under .context/sessions/. "
            "Use this to find prior session notes relevant to a topic, then pass their "
            "paths to `load_context_files` — do not rely on this tool's "
            "snippets alone."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "query": {"type": "string", "description": "Natural language search query"},
                "n_results": {"type": "integer", "default": 5},
            },
            "required": ["project_path", "query"],
        },
        output_schema=_SEARCH_OUTPUT_SCHEMA,
    ),
    Tool(
        name="find_latest_session_file",
        description=(
            "Deterministically find the most recent .context/sessions/*.md file "
            "(sorted by filename, not semantic relevance). Pass the returned path "
            "to `load_context_files` to load it — do not rely on this tool's "
            "snippets alone."
        ),
        input_schema={
            "type": "object",
            "properties": {"project_path": _PROJECT_PATH_PROPERTY},
            "required": ["project_path"],
        },
    ),
    Tool(
        name="load_context_files",
        description=(
            "Load specific .context/-relative files into the active context. "
            "Each loaded file is tagged with its path and a SHA-512 hash of its "
            "contents so `reload_active_context_file` can later detect changes. "
            "Only pass files you actually need — do not load the whole .context/ tree."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of .context/-relative file paths to load, e.g. 'decisions/0007-use-pgvector.md'.",
                },
            },
            "required": ["project_path", "files"],
        },
    ),
    Tool(
        name="reload_active_context_file",
        description=(
            "Check whether files currently held in active context (previously loaded via "
            "`load_context_files`) have changed on disk, by comparing their known SHA-512 "
            "hash against the current one. Returns fresh tagged content for changed files, "
            "a short 'no change' message for unchanged files, and 'not found' for deleted files."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": _PROJECT_PATH_PROPERTY,
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "known_sha512": {"type": "string"},
                        },
                        "required": ["path", "known_sha512"],
                    },
                    "description": "List of {path, known_sha512} entries for files currently in active context.",
                },
            },
            "required": ["project_path", "files"],
        },
    ),
    Tool(
        name="save_session_summary",
        description=(
            "Save a summary of the current session to .context/sessions/YYYY-MM-DD.md. "
            "Call this at the end of a session with a concise summary of what was done."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "project_path": {"type": "string"},
                "summary": {
                    "type": "string",
                    "description": "Markdown summary: what was worked on, decisions made, next steps.",
                },
            },
            "required": ["project_path", "summary"],
        },
    ),
    Tool(
        name="index_project_context",
        description=(
            "Re-index the .context/ directory into the vector store. "
            "Run this after updating project.md, adding ADRs, or refreshing BUNDLE.md."
        ),
        input_schema={
            "type": "object",
            "properties": {"project_path": {"type": "string"}},
            "required": ["project_path"],
        },
    ),
    Tool(
        name="list_repositories",
        description=(
            "List repositories accessible via the configured repository provider. "
            "In multi-tenant deployments, use this to discover which repositories are "
            "available before calling other tools.  Optionally filter by organisation name."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "org": {
                    "type": "string",
                    "description": "Optional: filter results to repositories in this organisation.",
                }
            },
            "required": [],
        },
    ),
]

_TOOL_HANDLERS = {
    "search_context_index": search_context_index.handle,
    "search_adr_index": search_adr_index.handle,
    "search_session_files": search_session_files.handle,
    "find_latest_session_file": find_latest_session_file.handle,
    "load_context_files": load_context_files.handle,
    "reload_active_context_file": reload_active_context_file.handle,
    "save_session_summary": save_session.handle,
    "index_project_context": index_context.handle,
    "list_repositories": list_repositories.handle,
}


async def list_tools(ctx: ServerRequestContext, params: PaginatedRequestParams | None) -> ListToolsResult:
    """List the MCP tools exposed by this context_server.

    :return: (list) The registered ``Tool`` definitions advertised to MCP clients.
    """
    return ListToolsResult(tools=_TOOL_DEFINITIONS)


async def call_tool(ctx: ServerRequestContext, params: CallToolRequestParams) -> CallToolResult:
    """Dispatch an MCP tool call to its registered handler.

    :param name: (str) The name of the tool to invoke.
    :param arguments: (dict) The arguments supplied by the MCP client for this tool call.
    :return: (CallToolResult) The handler's result normalised into a ``CallToolResult``,
        or a single error message if ``name`` does not match a registered tool.
    """
    handler = _TOOL_HANDLERS.get(params.name)
    if not handler:
        return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {params.name}")])
    try:
        result = await handler(params.arguments)
    except Exception as exc:
        logger.exception("Tool '%s' raised an unhandled exception", params.name)
        return CallToolResult(content=[TextContent(type="text", text=str(exc))], is_error=True)
    if isinstance(result, CallToolResult):
        return result
    return CallToolResult(content=result)


async def _main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport == "stdio":
        from mcp_project_context_server.transport.stdio import run_stdio

        await run_stdio(context_server)

    elif transport == "sse":
        from mcp_project_context_server.transport.sse import run_sse

        await run_sse(context_server)

    else:
        raise EnvironmentError(f"Unsupported MCP_TRANSPORT value '{transport}'.  " "Supported values are: stdio, sse")


def run() -> None:
    """Start the MCP server, selecting transport via the ``MCP_TRANSPORT`` env var."""
    logger.info("project-context-server starting")
    try:
        asyncio.run(_main())
    except Exception:
        logger.exception("Server crashed at top level")
        raise


context_server = Server(
    name="project-context",
    version=__version__,
    description=(
        "Project Context Server.  Provides access to project context, "
        "including repomix BUNDLED.md, project.md, ADRs, and session summaries."
        "Use as the primary tool for AI-assisted development, and as the source "
        "of truth for decisions on project development."
    ),
    on_list_tools=list_tools,
    on_call_tool=call_tool,
)
````

## File: .gitignore
````
# Default ignored files
/shelf/
/workspace.xml
# Editor-based HTTP Client requests
/httpRequests/
# Ignored default folder with query files
/queries/
# Datasource local storage ignored files
/dataSources/
/dataSources.local.xml

dist/*
*.iml
.coverage
coverage.xml
build/*
**/*.egg-info
.idea/workspace.xml
.claude/settings.local.json
src/**/_version.py
AGENT.md
# Virtual environment
.venv/
venv/
*.pyc
__pycache__/
.env*
````

## File: README.md
````markdown
# MCP Project Context Server

<p align="center">
  <em>A Python MCP server that gives LLMs persistent, searchable access to project context — documentation, architecture decisions, and session notes.</em>
</p>

<div align="center">

[![License](https://img.shields.io/badge/License-AGPL%20v3-purple.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/mcp-project-context-server)](https://pypi.org/project/mcp-project-context-server/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-project-context-server)](https://pypi.org/project/mcp-project-context-server/)
[![Version](https://img.shields.io/pypi/v/mcp-project-context-server?label=version)](https://pypi.org/project/mcp-project-context-server/)  
[![Downloads](https://img.shields.io/pypi/dm/mcp-project-context-server)](https://pypi.org/project/mcp-project-context-server/)
[![Coverage](https://img.shields.io/badge/coverage-80%25-green.svg)](https://codecov.io/your-org/mcp-project-context-server)
[![Last Commit](https://img.shields.io/github/last-commit/DarkMatterProductions/mcp-project-context-server)]()
[![Issues](https://img.shields.io/github/issues/DarkMatterProductions/mcp-project-context-server)](https://github.com/DarkMatterProductions/mcp-project-context-server/issues)

</div>

---

## 📖 About the Server

**MCP Project Context Server** provides a robust, production-ready Model Context Protocol (MCP) server implementation designed to give Large Language Models (LLMs) persistent, searchable access to your project's contextual information.

### Core Capabilities

- **🔍 Semantic Search Engine**: Query your project documentation using natural language
- **📚 Persistent Knowledge Base**: Store and retrieve information from `.context/` directory structure
- **🏗️ Modular Architecture**: Pluggable embedding providers, vector stores, and repository providers
- **🎯 ADR Integration**: Full support for Architecture Decision Records with lifecycle management
- **📝 Session Tracking**: Record and retrieve session notes for future reference
- **🔄 Easy Reindexing**: Rebuild your knowledge base with a single command

### Key Features

- ✅ **Multi-Provider Embedding**: Ollama, Voyage AI, OpenAI, Cohere, Google Gemini, and Google Vertex AI
- ✅ **Flexible Vector Storage**: ChromaDB (local or HTTP) and pgvector (PostgreSQL)
- ✅ **Multiple Repository Providers**: Local filesystem, GitHub, GitLab, and Gitea
- ✅ **Transport Options**: stdio (default) and HTTP/SSE for remote deployments
- ✅ **Configuration-Free**: Environment variable-based setup, no hardcoded paths
- ✅ **Cross-Platform**: Works on Windows, macOS, and Linux
- ✅ **Async-First**: All operations use async/await for performance and scalability
- ✅ **Error-Resilient**: Graceful error handling with informative messaging

---

## 📋 Table of Contents

- [About the Server](#-about-the-server)
- [Prerequisites](#-Prerequisites)
- [Installation](#-installation)
- [Embedding Providers](#-embedding-providers)
  - [Ollama](#ollama)
  - [Voyage AI](#voyage-ai)
  - [OpenAI](#openai)
  - [Cohere](#cohere)
  - [Google Gemini](#google-gemini)
  - [Google Vertex AI](#google-vertex-ai)
- [Vector Stores](#️-vector-stores)
  - [ChromaDB Local (Default)](#chromadb-local-default)
  - [ChromaDB HTTP](#chromadb-http)
  - [pgvector (PostgreSQL)](#pgvector-postgresql)
- [Repository Providers](#-repository-providers)
  - [Local Filesystem (Default)](#local-filesystem-default)
  - [GitHub](#github)
  - [GitLab](#gitlab)
  - [Gitea](#gitea)
  - [Multi-Tenant Mode](#multi-tenant-mode)
- [Transport](#-transport)
  - [stdio (Default)](#stdio-default)
  - [HTTP/SSE](#httpsse)
- [Client Setup](#️-client-setup)
  - [Claude Desktop](#claude-desktop)
  - [Claude Code](#claude-code)
  - [Cursor](#cursor)
  - [Continue](#continue)
  - [Windsurf](#windsurf)
  - [VS Code Copilot](#vs-code-copilot)
- [Tools Reference](#️-tools-reference)
- [Environment Variables Reference](#-environment-variables-reference)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## Prerequisites

Before installing, ensure you have:

- **Python 3.11+** installed
- **Ollama** running with an embedding model (e.g., `nomic-embed-text`)
- At least **2GB RAM** available
- **4.5GB disk space** for ChromaDB (minimum)

## 🚀 Installation

### Core Package

```bash
pip install mcp-project-context-server
```

The core package contains the server, tools, and ChromaDB local integration. It does **not** bundle any embedding provider SDK. You must install the extra for your chosen provider.

### Embedding Provider Extras

Install the extra that matches your chosen embedding provider:

| Provider | Extra | Install Command |
|----------|-------|-----------------|
| Ollama (local, no API key) | `ollama` | `pip install "mcp-project-context-server[ollama]"` |
| Voyage AI | `voyage` | `pip install "mcp-project-context-server[voyage]"` |
| OpenAI | `openai` | `pip install "mcp-project-context-server[openai]"` |
| Cohere | `cohere` | `pip install "mcp-project-context-server[cohere]"` |
| Google Gemini | `google` | `pip install "mcp-project-context-server[google]"` |
| Google Vertex AI | `google-vertex` | `pip install "mcp-project-context-server[google-vertex]"` |

### Vector Store Extras

ChromaDB (local and HTTP) is included in the core package. Install the `pgvector` extra only if you are using PostgreSQL:

```bash
pip install "mcp-project-context-server[pgvector]"
```

### HTTP/SSE Transport Extra

Required only when running the server over HTTP/SSE (remote deployments, Google Agent Engine, etc.):

```bash
pip install "mcp-project-context-server[sse]"
```

### Combining Extras

Multiple extras can be combined in a single install:

```bash
# Ollama with pgvector
pip install "mcp-project-context-server[ollama,pgvector]"

# OpenAI with SSE transport
pip install "mcp-project-context-server[openai,sse]"

# Cohere with pgvector and SSE
pip install "mcp-project-context-server[cohere,pgvector,sse]"
```

### Install Everything

```bash
pip install "mcp-project-context-server[all]"
```

### From Source

```bash
git clone https://github.com/DarkMatterProductions/mcp-project-context-server.git
cd mcp-project-context-server
pip install -e ".[ollama]"  # Replace with your chosen provider extra
```

---

## 🔌 Embedding Providers

The embedding provider is selected by the `EMBED_PROVIDER` environment variable. **This variable is required** — the server will not start without it.

```bash
export EMBED_PROVIDER=ollama  # Replace with your chosen provider
```

Supported values: `ollama`, `voyage`, `openai`, `cohere`, `google`, `vertexai`

---

### Ollama

Ollama runs embedding models locally. No API key is required.

**Install:**

```bash
pip install "mcp-project-context-server[ollama]"
```

**Prerequisites:** [Install Ollama](https://ollama.com/download) and pull an embedding model:

```bash
ollama pull nomic-embed-text
```

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `ollama` |
| `OLLAMA_HOST` | `http://localhost:11434` | URL of the Ollama server |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=ollama
export OLLAMA_HOST=http://localhost:11434    # Optional — this is the default
export OLLAMA_EMBED_MODEL=nomic-embed-text  # Optional — this is the default
```

**Popular models:**

| Model | Size | Notes |
|-------|------|-------|
| `nomic-embed-text` | ~274 MB | Fast, good general purpose |
| `mxbai-embed-large` | ~669 MB | Higher quality |
| `all-minilm` | ~46 MB | Lightweight, lower quality |

---

### Voyage AI

Voyage AI provides embedding models optimized for code and technical content.

**Install:**

```bash
pip install "mcp-project-context-server[voyage]"
```

**Getting an API Key:**

1. Sign up at [voyageai.com](https://www.voyageai.com/)
2. Navigate to **Dashboard → API Keys**
3. Click **Create new key**, give it a name, and copy the key value

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `voyage` |
| `VOYAGE_API_KEY` | — | **Required.** Your Voyage AI API key |
| `VOYAGE_EMBED_MODEL` | `voyage-code-3` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=voyage
export VOYAGE_API_KEY=pa-...
export VOYAGE_EMBED_MODEL=voyage-code-3  # Optional
```

**Recommended models:**

| Model | Notes |
|-------|-------|
| `voyage-code-3` | Code-optimized, default |
| `voyage-3` | General purpose |
| `voyage-3-lite` | Faster, lower cost |

---

### OpenAI

**Install:**

```bash
pip install "mcp-project-context-server[openai]"
```

**Getting an API Key:**

1. Sign up or log in at [platform.openai.com](https://platform.openai.com/)
2. Navigate to **Dashboard → API Keys**
3. Click **Create new secret key**, give it a name, and copy the key immediately — it is only shown once

> **Billing note:** OpenAI API access is pay-per-use. Add a payment method at [platform.openai.com/account/billing](https://platform.openai.com/account/billing) before your free credits run out.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `openai` |
| `OPENAI_API_KEY` | — | **Required.** Your OpenAI API key |
| `OPENAI_EMBED_MODEL` | `text-embedding-3-small` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export OPENAI_EMBED_MODEL=text-embedding-3-small  # Optional
```

**Recommended models:**

| Model | Dimensions | Notes |
|-------|-----------|-------|
| `text-embedding-3-small` | 1536 | Fast, cost-effective, default |
| `text-embedding-3-large` | 3072 | Highest quality |

---

### Cohere

**Install:**

```bash
pip install "mcp-project-context-server[cohere]"
```

**Getting an API Key:**

1. Sign up or log in at [dashboard.cohere.com](https://dashboard.cohere.com/)
2. Navigate to **API Keys** in the left sidebar
3. Click **New Trial Key** (free tier, rate-limited) or **New Production Key**, then copy the value

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `cohere` |
| `COHERE_API_KEY` | — | **Required.** Your Cohere API key |
| `COHERE_EMBED_MODEL` | `embed-english-v3.0` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=cohere
export COHERE_API_KEY=...
export COHERE_EMBED_MODEL=embed-english-v3.0  # Optional
```

**Recommended models:**

| Model | Notes |
|-------|-------|
| `embed-english-v3.0` | English, default |
| `embed-multilingual-v3.0` | 100+ languages |

---

### Google Gemini

Uses the Google AI Studio API (Gemini embedding models).

**Install:**

```bash
pip install "mcp-project-context-server[google]"
```

**Getting an API Key:**

1. Sign in at [aistudio.google.com](https://aistudio.google.com/)
2. Click **Get API key** in the top navigation
3. Click **Create API key** — choose an existing Google Cloud project or create a new one
4. Copy the generated key

> **Note:** Google AI Studio keys are suitable for development and personal use. For production workloads with higher quotas and enterprise SLAs, use [Google Vertex AI](#google-vertex-ai) instead.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `google` |
| `GOOGLE_API_KEY` | — | **Required.** Your Google AI Studio API key |
| `GOOGLE_EMBED_MODEL` | `text-embedding-004` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=google
export GOOGLE_API_KEY=AIza...
export GOOGLE_EMBED_MODEL=text-embedding-004  # Optional
```

---

### Google Vertex AI

Uses the Vertex AI SDK with Google Cloud Application Default Credentials (ADC). No API key is required — authentication is handled through your Google Cloud identity.

**Install:**

```bash
pip install "mcp-project-context-server[google-vertex]"
```

**Prerequisites:**

1. **Enable the Vertex AI API** in your Google Cloud project:
   - Open [console.cloud.google.com/apis/library](https://console.cloud.google.com/apis/library)
   - Search for **Vertex AI API** and click **Enable**

2. **Authenticate** using Application Default Credentials. For local development:

   ```bash
   gcloud auth application-default login
   ```

   For production environments (e.g. Cloud Run, GKE), assign a service account with the **Vertex AI User** role (`roles/aiplatform.user`) to your workload, and set `GOOGLE_APPLICATION_CREDENTIALS` if using a key file.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBED_PROVIDER` | — | Must be set to `vertexai` |
| `VERTEXAI_PROJECT` | — | **Required.** Your Google Cloud project ID |
| `VERTEXAI_LOCATION` | — | **Required.** Google Cloud region (e.g. `us-central1`) |
| `VERTEXAI_EMBED_MODEL` | `text-embedding-004` | Embedding model to use |

**Example:**

```bash
export EMBED_PROVIDER=vertexai
export VERTEXAI_PROJECT=my-gcp-project-id
export VERTEXAI_LOCATION=us-central1
export VERTEXAI_EMBED_MODEL=text-embedding-004  # Optional
```

---

## 🗄️ Vector Stores

The vector store is selected by the `VECTOR_STORE_PROVIDER` environment variable. Defaults to `chroma-local`.

Supported values: `chroma-local`, `chroma-http`, `pgvector`

---

### ChromaDB Local (Default)

Persists embeddings in a local directory. Included in the core package — no extra installation required.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `VECTOR_STORE_PROVIDER` | `chroma-local` | Set to `chroma-local` or omit |
| `CHROMA_DIR` | `~/.mcp-data/chroma` | Directory where ChromaDB stores its data |

**Example:**

```bash
export VECTOR_STORE_PROVIDER=chroma-local  # Optional — this is the default
export CHROMA_DIR=~/.mcp-data/chroma       # Optional — this is the default
```

---

### ChromaDB HTTP

Connects to a remote or containerized ChromaDB instance over HTTP.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `VECTOR_STORE_PROVIDER` | `chroma-local` | Must be set to `chroma-http` |
| `CHROMA_HOST` | `localhost` | ChromaDB server hostname |
| `CHROMA_PORT` | `8000` | ChromaDB server port |
| `CHROMA_API_KEY` | _(none)_ | API key for ChromaDB Cloud or authenticated instances |

**Example:**

```bash
export VECTOR_STORE_PROVIDER=chroma-http
export CHROMA_HOST=chroma.example.com
export CHROMA_PORT=8000
export CHROMA_API_KEY=your-chroma-api-key  # Optional
```

---

### pgvector (PostgreSQL)

Stores embeddings in a PostgreSQL database using the `pgvector` extension.

**Install:**

```bash
pip install "mcp-project-context-server[pgvector]"
```

**Prerequisites:** A PostgreSQL instance (13+) with the `pgvector` extension enabled:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `VECTOR_STORE_PROVIDER` | `chroma-local` | Must be set to `pgvector` |
| `PGVECTOR_CONNECTION_STRING` | — | **Required.** PostgreSQL connection string |

**Example:**

```bash
export VECTOR_STORE_PROVIDER=pgvector
export PGVECTOR_CONNECTION_STRING=postgresql://user:password@localhost:5432/mydb
```

---

## 📁 Repository Providers

The repository provider controls where the server reads project files from. Defaults to `local`.

Supported values: `local`, `github`, `gitlab`, `gitea`

---

### Local Filesystem (Default)

Reads files from the local filesystem. No additional configuration required.

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO_PROVIDER` | `local` | Set to `local` or omit |
| `PROJECT_PATH` | _(from tool call)_ | Override the project path at server startup |

---

### GitHub

Reads files from GitHub repositories via the GitHub REST API.

**Getting a Personal Access Token:**

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)** or **Fine-grained personal access tokens**
   - Classic: grant the `repo` scope (or `public_repo` for public repositories only)
   - Fine-grained: grant **Contents: Read-only** on the target repositories
3. Copy the generated token

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO_PROVIDER` | `local` | Must be set to `github` |
| `REPO_AUTH_TOKEN` | _(empty)_ | GitHub personal access token. Required for private repos |
| `REPO_BASE_URL` | `https://api.github.com` | Override for GitHub Enterprise Server |
| `REPO_DEFAULT_BRANCH` | `main` | Default branch when none is specified |

**Example:**

```bash
export REPO_PROVIDER=github
export REPO_AUTH_TOKEN=ghp_...

# GitHub Enterprise only:
export REPO_BASE_URL=https://github.example.com/api/v3
```

---

### GitLab

Reads files from GitLab repositories via the GitLab REST API.

**Getting a Personal Access Token:**

1. Navigate to **User Settings → Access Tokens** (profile menu → Edit profile → Access Tokens)
2. Click **Add new token**
3. Grant at minimum the `read_api` scope
4. Set an expiry date and click **Create personal access token**
5. Copy the token immediately — it is not shown again

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO_PROVIDER` | `local` | Must be set to `gitlab` |
| `REPO_AUTH_TOKEN` | _(empty)_ | GitLab personal access token |
| `REPO_BASE_URL` | `https://gitlab.com` | Override for self-hosted GitLab instances |
| `REPO_DEFAULT_BRANCH` | `main` | Default branch when none is specified |

**Example:**

```bash
export REPO_PROVIDER=gitlab
export REPO_AUTH_TOKEN=glpat-...

# Self-hosted GitLab only:
export REPO_BASE_URL=https://gitlab.example.com
```

---

### Gitea

Reads files from self-hosted Gitea instances. `REPO_BASE_URL` is required.

**Getting an Access Token:**

1. Log in to your Gitea instance
2. Go to **Settings → Applications** (your user avatar → Settings → Applications)
3. Under **Manage Access Tokens**, enter a name, select the desired permissions, and click **Generate Token**
4. Copy the generated token — it is only shown once

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO_PROVIDER` | `local` | Must be set to `gitea` |
| `REPO_BASE_URL` | — | **Required.** Your Gitea instance URL (e.g. `https://gitea.example.com`) |
| `REPO_AUTH_TOKEN` | _(empty)_ | Gitea access token |
| `REPO_DEFAULT_BRANCH` | `main` | Default branch when none is specified |

**Example:**

```bash
export REPO_PROVIDER=gitea
export REPO_BASE_URL=https://gitea.example.com
export REPO_AUTH_TOKEN=...
```

---

### Multi-Tenant Mode

All repository providers support multi-tenant mode, which restricts file access to an allowlist of approved organizations and repositories. Enable it with `REPO_MULTI_TENANT=true`.

At least one of `APPROVED_ORGS` or `APPROVED_REPOS` must be set when multi-tenant mode is active.

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO_MULTI_TENANT` | `false` | Set to `true` to enable allowlist enforcement |
| `APPROVED_ORGS` | _(none)_ | Comma-separated list of approved organization names |
| `APPROVED_REPOS` | _(none)_ | Comma-separated list of approved `owner/repo` identifiers |

**Example:**

```bash
export REPO_MULTI_TENANT=true
export APPROVED_ORGS=my-org,partner-org
export APPROVED_REPOS=other-org/specific-repo
```

---

## 🚌 Transport

The transport is selected by the `MCP_TRANSPORT` environment variable. Defaults to `stdio`.

---

### stdio (Default)

Standard input/output transport. Compatible with Claude Desktop, Claude Code, Cursor, Continue, VS Code Copilot, and most other MCP clients. No additional installation or configuration required.

```bash
export MCP_TRANSPORT=stdio  # Optional — this is the default
project-context-server
```

---

### HTTP/SSE

HTTP/SSE transport for remote deployments, team servers, and cloud integrations.

**Install:**

```bash
pip install "mcp-project-context-server[sse]"
```

**Start the server:**

```bash
export MCP_TRANSPORT=sse
export MCP_HOST=0.0.0.0  # Optional — default is 0.0.0.0
export MCP_PORT=8080      # Optional — default is 8080
project-context-server
```

The server exposes two endpoints:
- `GET /sse` — SSE connection endpoint for MCP clients
- `GET /health` — unauthenticated health check

**Authentication:**

| `MCP_AUTH_TYPE` | Description |
|-----------------|-------------|
| `none` | No authentication. Use only on trusted private networks. |
| `bearer` | Static token via `Authorization: Bearer <token>`. Requires `MCP_AUTH_TOKEN`. |
| `google-iam` | Google Cloud identity token validation. For use with Agent Engine and service-to-service calls. |

**Bearer token example:**

```bash
export MCP_TRANSPORT=sse
export MCP_AUTH_TYPE=bearer
export MCP_AUTH_TOKEN=your-secret-token
project-context-server
```

**Google IAM example:**

```bash
export MCP_TRANSPORT=sse
export MCP_AUTH_TYPE=google-iam
export GOOGLE_IAM_AUDIENCE=https://my-service.example.com     # Recommended
export GOOGLE_APPROVED_SERVICE_ACCOUNTS=sa@project.iam.gserviceaccount.com  # Optional allowlist
project-context-server
```

**SSE environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `stdio` | Must be set to `sse` |
| `MCP_HOST` | `0.0.0.0` | Bind address |
| `MCP_PORT` | `8080` | Listen port |
| `MCP_AUTH_TYPE` | `none` | Authentication: `none`, `bearer`, `google-iam` |
| `MCP_AUTH_TOKEN` | — | Required when `MCP_AUTH_TYPE=bearer` |
| `GOOGLE_IAM_AUDIENCE` | _(none)_ | Expected `aud` claim in Google identity tokens |
| `GOOGLE_SERVICE_ACCOUNT_KEY_PATH` | _(none)_ | Path to service account JSON key (uses ADC if unset) |
| `GOOGLE_APPROVED_SERVICE_ACCOUNTS` | _(none)_ | Comma-separated allowed caller service account emails |

---

## 🖥️ Client Setup

The examples below use **Ollama** as the embedding provider and **ChromaDB local** as the vector store — the simplest setup with no API key requirements. Substitute environment variables for your chosen providers using the reference in [Embedding Providers](#-embedding-providers) and [Vector Stores](#️-vector-stores).

> **Detailed client docs** with full per-provider configuration matrices are available in [`docs/clients/`](docs/clients/). Those docs are currently being updated to correct some environment variable names from the old implementation — see [`docs/client-setup-expansion.md`](docs/client-setup-expansion.md) for status and the correct variable reference.

---

### Claude Desktop

1. **Install the server:**

   ```bash
   pip install "mcp-project-context-server[ollama]"
   ```

2. **Locate the config file** for your OS:

   | OS | Config File |
   |----|-------------|
   | **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
   | **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
   | **Linux** | `~/.config/Claude/claude_desktop_config.json` |

3. **Add the server** to `claude_desktop_config.json`:

   **Windows:**

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     }
   }
   ```

   **macOS / Linux:**

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop** and verify the server appears in the MCP tools list.

---

### Claude Code

1. **Install the server:**

   ```bash
   pip install "mcp-project-context-server[ollama]"
   ```

2. **Add the MCP server** using one of two methods:

   **Option A — CLI:**

   ```bash
   claude mcp add project-context \
     -e EMBED_PROVIDER=ollama \
     -e OLLAMA_HOST=http://localhost:11434 \
     -e OLLAMA_EMBED_MODEL=nomic-embed-text \
     -- python -m mcp_project_context_server
   ```

   **Option B — Config file:**

   | Scope | Location |
   |-------|----------|
   | **User (global)** | `~/.claude.json` |
   | **Project** | `.claude/settings.json` (in project root) |

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     }
   }
   ```

3. **Verify the server is connected:**

   ```bash
   claude mcp list
   ```

---

### Cursor

1. **Install the server** (see [Installation](#-installation))

2. **Choose a config scope:**

   | Scope | Windows | macOS / Linux |
   |-------|---------|---------------|
   | **Global** | `%USERPROFILE%\.cursor\mcp.json` | `~/.cursor/mcp.json` |
   | **Project** | `.cursor\mcp.json` (project root) | `.cursor/mcp.json` (project root) |

3. **Configure `mcp.json`:**

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     }
   }
   ```

4. **Reload Cursor** and use `@project-context` in the chat panel.

---

### Continue

1. **Install the Continue extension** for VS Code or JetBrains

2. **Locate the config file:**

   | OS | Config File |
   |----|-------------|
   | **Windows** | `%USERPROFILE%\.continue\config.yaml` |
   | **macOS / Linux** | `~/.continue/config.yaml` |

3. **Add to `config.yaml`:**

   ```yaml
   mcpServers:
     - name: project-context
       command: python
       args:
         - "-m"
         - mcp_project_context_server
       env:
         EMBED_PROVIDER: "ollama"
         OLLAMA_HOST: "http://localhost:11434"
         OLLAMA_EMBED_MODEL: "nomic-embed-text"
   ```

   Or if using `config.json`:

   ```json
   {
     "mcpServers": [
       {
         "name": "project-context",
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     ]
   }
   ```

---

### Windsurf

1. **Install the server** (see [Installation](#-installation))

2. **Locate the MCP config file:**

   | OS | Config File |
   |----|-------------|
   | **Windows** | `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
   | **macOS / Linux** | `~/.codeium/windsurf/mcp_config.json` |

3. **Configure `mcp_config.json`** (create if it does not exist):

   ```json
   {
     "mcpServers": {
       "project-context": {
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     }
   }
   ```

4. **Restart Windsurf** and verify the server appears under **Settings → MCP Servers**.

---

### VS Code Copilot

MCP support is built into VS Code via **GitHub Copilot** (no separate extension required). Requires VS Code 1.99+ with the Copilot extension.

1. **Install the server** (see [Installation](#-installation))

2. **Choose a config scope:**

   **Option A — Workspace (`.vscode/mcp.json`):**

   ```json
   {
     "servers": {
       "project-context": {
         "type": "stdio",
         "command": "python",
         "args": ["-m", "mcp_project_context_server"],
         "env": {
           "EMBED_PROVIDER": "ollama",
           "OLLAMA_HOST": "http://localhost:11434",
           "OLLAMA_EMBED_MODEL": "nomic-embed-text"
         }
       }
     }
   }
   ```

   **Option B — User settings (`settings.json`):**

   ```json
   {
     "mcp": {
       "servers": {
         "project-context": {
           "type": "stdio",
           "command": "python",
           "args": ["-m", "mcp_project_context_server"],
           "env": {
             "EMBED_PROVIDER": "ollama",
             "OLLAMA_HOST": "http://localhost:11434",
             "OLLAMA_EMBED_MODEL": "nomic-embed-text"
           }
         }
       }
     }
   }
   ```

3. **Use in Copilot Chat** by switching to **Agent mode** — MCP tools are available automatically.

---

## 🛠️ Tools Reference

| Tool | Description |
|------|-------------|
| `index_project_context` | Indexes all files in `.context/` into the configured vector store |
| `search_project_context` | Performs semantic search over indexed context |
| `load_project_context` | Returns the full contents of `.context/` (project overview, ADRs, latest session) |
| `save_session_summary` | Writes a session note to `.context/sessions/YYYY-MM-DD.md` |
| `list_repositories` | Lists available repositories via the configured repository provider |

### Usage Examples

```python
# Semantic search
search_project_context(
    query="How do we handle authentication?",
    n_results=5
)

# Load full context
load_project_context()
# Returns: project.md, all ADRs, latest session file

# Save session notes
save_session_summary(
    summary="Investigated chunking strategy alternatives, decided on fixed-size for now"
)

# Rebuild the index
index_project_context()
```

---

## 🌐 Environment Variables Reference

### Embedding Providers

| Variable | Provider | Default | Required |
|----------|----------|---------|----------|
| `EMBED_PROVIDER` | All | — | Yes |
| `OLLAMA_HOST` | `ollama` | `http://localhost:11434` | No |
| `OLLAMA_EMBED_MODEL` | `ollama` | `nomic-embed-text` | No |
| `VOYAGE_API_KEY` | `voyage` | — | Yes |
| `VOYAGE_EMBED_MODEL` | `voyage` | `voyage-code-3` | No |
| `OPENAI_API_KEY` | `openai` | — | Yes |
| `OPENAI_EMBED_MODEL` | `openai` | `text-embedding-3-small` | No |
| `COHERE_API_KEY` | `cohere` | — | Yes |
| `COHERE_EMBED_MODEL` | `cohere` | `embed-english-v3.0` | No |
| `GOOGLE_API_KEY` | `google` | — | Yes |
| `GOOGLE_EMBED_MODEL` | `google` | `text-embedding-004` | No |
| `VERTEXAI_PROJECT` | `vertexai` | — | Yes |
| `VERTEXAI_LOCATION` | `vertexai` | — | Yes |
| `VERTEXAI_EMBED_MODEL` | `vertexai` | `text-embedding-004` | No |

### Vector Stores

| Variable | Store | Default | Required |
|----------|-------|---------|----------|
| `VECTOR_STORE_PROVIDER` | All | `chroma-local` | No |
| `CHROMA_DIR` | `chroma-local` | `~/.mcp-data/chroma` | No |
| `CHROMA_HOST` | `chroma-http` | `localhost` | No |
| `CHROMA_PORT` | `chroma-http` | `8000` | No |
| `CHROMA_API_KEY` | `chroma-http` | _(none)_ | No |
| `PGVECTOR_CONNECTION_STRING` | `pgvector` | — | Yes (for pgvector) |

### Repository Providers

| Variable | Provider | Default | Required |
|----------|----------|---------|----------|
| `REPO_PROVIDER` | All | `local` | No |
| `PROJECT_PATH` | `local` | _(from tool call)_ | No |
| `REPO_AUTH_TOKEN` | `github`, `gitlab`, `gitea` | _(empty)_ | No (required for private repos) |
| `REPO_BASE_URL` | `github`, `gitlab`, `gitea` | _(provider default)_ | Yes for `gitea` |
| `REPO_DEFAULT_BRANCH` | `github`, `gitlab`, `gitea` | `main` | No |
| `REPO_MULTI_TENANT` | All | `false` | No |
| `APPROVED_ORGS` | All (multi-tenant) | _(none)_ | Yes (if multi-tenant, with no APPROVED_REPOS) |
| `APPROVED_REPOS` | All (multi-tenant) | _(none)_ | Yes (if multi-tenant, with no APPROVED_ORGS) |

### Transport

| Variable | Default | Required |
|----------|---------|----------|
| `MCP_TRANSPORT` | `stdio` | No |
| `MCP_HOST` | `0.0.0.0` | No |
| `MCP_PORT` | `8080` | No |
| `MCP_AUTH_TYPE` | `none` | No |
| `MCP_AUTH_TOKEN` | — | Yes (if `MCP_AUTH_TYPE=bearer`) |
| `GOOGLE_IAM_AUDIENCE` | _(none)_ | No |
| `GOOGLE_SERVICE_ACCOUNT_KEY_PATH` | _(none)_ | No |
| `GOOGLE_APPROVED_SERVICE_ACCOUNTS` | _(none)_ | No |

---

## 📂 Project Structure

```
mcp-project-context-server/
├── src/mcp_project_context_server/
│   ├── server.py                       # MCP server entry point and tool registry
│   ├── exceptions.py                   # Shared exception types
│   ├── tools/
│   │   ├── index_context.py            # index_project_context tool
│   │   ├── search_context.py           # search_project_context tool
│   │   ├── load_context.py             # load_project_context tool
│   │   ├── save_session.py             # save_session_summary tool
│   │   └── list_repositories.py        # list_repositories tool
│   ├── integrations/
│   │   ├── embeddings/
│   │   │   ├── base.py                 # EmbeddingProvider Protocol
│   │   │   ├── registry.py             # Provider factory (EMBED_PROVIDER)
│   │   │   ├── ollama/client.py
│   │   │   ├── voyage/client.py
│   │   │   ├── openai/client.py
│   │   │   ├── cohere/client.py
│   │   │   ├── google/client.py
│   │   │   └── vertexai/client.py
│   │   ├── vectorstore/
│   │   │   ├── base.py                 # VectorStoreProvider Protocol
│   │   │   ├── registry.py             # Provider factory (VECTOR_STORE_PROVIDER)
│   │   │   ├── chroma_local/client.py
│   │   │   ├── chroma_http/client.py
│   │   │   └── pgvector/client.py
│   │   ├── repository/
│   │   │   ├── base.py                 # RepositoryProvider Protocol
│   │   │   ├── registry.py             # Provider factory (REPO_PROVIDER)
│   │   │   ├── local/client.py
│   │   │   ├── github/client.py
│   │   │   ├── gitlab/client.py
│   │   │   └── gitea/client.py
│   │   └── transport/
│   │       ├── stdio.py
│   │       └── sse.py
│   └── helpers/
│       └── context.py                  # Utility functions
├── .context/                            # Project context directory
│   ├── project.md                      # Project overview
│   ├── sessions/                       # Session notes
│   └── decisions/                      # Architecture Decision Records
├── tests/
│   ├── unit/                           # Unit tests (mocked dependencies)
│   └── integration/                    # Integration tests (real services)
├── docs/
│   └── client-setup-expansion.md       # Per-provider client setup expansion plan
├── README.md
├── CONTRIBUTING.md
├── pyproject.toml
└── LICENSE
```

---

## 🧪 Testing

### Run the Test Suite

```bash
# Install test dependencies
pip install "mcp-project-context-server[all]"
pip install pytest pytest-asyncio pytest-mock pytest-cov

# Unit tests (no external services required)
pytest tests/unit/

# Integration tests (requires a running embedding provider and vector store)
pytest tests/integration/

# All tests with coverage report
pytest --cov=src/mcp_project_context_server tests/
```

### Development Workflow

```bash
# Format and lint
black src/
isort src/
flake8 src/
mypy src/

# Check coverage
pytest --cov=src/mcp_project_context_server --cov-report=term-missing tests/unit/
```

---

## 🔮 Roadmap

- [ ] **Auto-reindex**: Watchdog-based file monitoring for automatic reindexing
- [ ] **Codebase Indexing**: Repomix integration for source code analysis
- [ ] **Enhanced ADR Tools**: First-class MCP tools for ADR lifecycle management
- [ ] **Batch Operations**: Bulk ADR updates and session imports
- [ ] **Provider Caching**: Singleton caching for embedding and vector store providers

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines including commit message standards, ADR requirements, and the PR process.

---

## 📝 License

This project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE Version 3 — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **MCP Team**: For the Model Context Protocol
- **ChromaDB**: For the embedded vector store
- **Ollama**: For local embedding model hosting

---

<div align="center">

**Built with ❤️ for better LLM project understanding**

</div>
````

## File: pyproject.toml
````toml
[project]
name = "mcp-project-context-server"
dynamic = [ "version",]
description = "A Python MCP server that gives LLMs persistent, searchable access to project context — documentation, architecture decisions, and session notes."
readme = "README.md"
license = {"file" = "LICENSE"}
authors = [
    {name = "James Boylan", email = "drahkar@darkmatter-productions.com"}
]
maintainers = [
    {name = "Darkmatter Productions", email = "pypi@darkmatter-productions.com"}
]
requires-python = ">=3.11"
keywords = [
    "mcp", "model-context-protocol", "semantic-search",
    "chromadb", "llm", "documentation", "adr", "architecture-decision-records",
    "vector-store", "python", "server"
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU Affero General Public License v3",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Artificial Intelligence"
]
dependencies = [
    "mcp>=2.1.1,<3",
    "chromadb",
    "watchdog",
    "httpx>=0.27",
    "starlette",
    "uvicorn",
]

[project.optional-dependencies]
# --- Embedding providers ---
ollama = ["ollama>=0.4.0"]
voyage = ["voyageai"]
openai = ["openai>=1.0"]
cohere = ["cohere>=5.0"]
google = ["google-generativeai"]
google-vertex = ["google-cloud-aiplatform"]

# --- Vector store providers ---
pgvector = ["asyncpg", "pgvector"]
gcp-vector-search = ["google-cloud-aiplatform", "google-cloud-firestore"]

# --- HTTP/SSE transport ---
sse = ["starlette", "uvicorn", "google-auth"]

# --- Repository providers ---
github = []        # uses httpx, already in core deps
gitlab = []        # uses httpx, already in core deps
gitea  = []        # uses httpx, already in core deps

# --- Everything ---
all = [
    "voyageai",
    "openai>=1.0",
    "cohere>=5.0",
    "google-generativeai",
    "google-cloud-aiplatform",
    "google-cloud-firestore",
    "asyncpg",
    "pgvector",
    "google-auth",
    "starlette",
    "uvicorn",
]

[dependency-groups]
testsuite = [
    "pytest>=9.0.3",
    "pytest-cov>=7.1.0",
    "pytest-order>=1.5.0",
    "pytest-mock>=3.15.1",
    "pytest-asyncio>=1.3.0",
    "pytest-benchmark>=4.0.0",
]

[tool.setuptools_scm]
version_scheme = "guess-next-dev"
local_scheme = "node-and-date"
#tag_regex = '^(?P<version>\d+\.\d+\.\d+[.dev\d+]*$'

[project.scripts]
project-context-server = "mcp_project_context_server.server:run"

[project.urls]
Homepage = "https://github.com/DarkMatterProductions/mcp-project-context-server"
Documentation = "https://github.com/DarkMatterProductions/mcp-project-context-server#readme"
Repository = "https://github.com/DarkMatterProductions/mcp-project-context-server.git"
Issues = "https://github.com/DarkMatterProductions/mcp-project-context-server/issues"
Changelog = "https://github.com/DarkMatterProductions/mcp-project-context-server/blob/main/CHANGELOG.md"

[build-system]
requires = ["setuptools>=64", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[tool.setuptools-scm]
write_to = "src/mcp_project_context_server/_version.py"


[tool.setuptools.packages.find]
where = ["src"]  # Look for packages in src/

[tool.setuptools.package-dir]
"" = "src"

[tool.pytest.ini_options]
pythonpath = [
    "src"
]
testpaths = [
    "tests"
]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
markers = [
    "external_services: marks tests that require ChromaDB and an embedding provider (e.g. Ollama). Skip with: -m 'not external_services'",
]

[tool.black]
line-length = 120
target-version = [
    'py39',
    'py310',
    'py311',
]
include = '\.py$'
exclude = '''
/(
    tests/resources
    | /src/*.egg-info/
)/
'''

[tool.flake8]
plugins = "flake8"
max-line-length = 120
extend-ignore = "E203, W503, E501"  # for Black compatibility
filename = '*.py,*'
exclude = [
    ".git",
    "__pycache__",
    "./src/*-info/*",
    "tests/resources"
]
ignore="D100,D104,D105,D200,D204,D205,D301,D302,D400,D401,D402,D403,D404,E203,E741,H101,H301,H306,H401,H404,H405,N804,N805,P102,W291,P302,S001,W503,W504,E122,W605,F541,E231,E241,E128,E501,E125,E126"
# IGNORE THESE ERRORS.
# D100: Missing docstring in public module
# D104: Missing docstring in public package
# D105: Missing docstring in magic method
# D200: One-line docstring should fit on one line with quotes
# D204: 1 blank line required after class docstring
# D205: 1 blank line required between summary line and description
# D301: Use r""" if any backslashes in a docstring
# D302: Use u""" for Unicode docstrings
# D400: First line should end with a period
# D401: First line should be in imperative mood
# D402: First line should not be the function's "signature"
# D403: First word of the first line should be properly capitalized
# D404: First word of the docstring should not be `This`
# E203: whitespace before the ':' character in slice syntax.
# E741 ambiguous variable name
# H301: one import per line
# H306: imports not in alphabetical order (time, os)
# H401: docstring should not start with a space
# H404: multi line docstring should start without a leading new line
# H405: multi line docstring summary not separated with an empty line
# N804: first argument of a classmethod should be named 'cls'
# N805: first argument of a method should be named 'self'
# P102: docstring does contain unindexed parameters
# P302: format call provides unused keyword (e.g. 'exc_info')
# S001: found module formatter
# W503: Line break before binary operator
# W504: line break after binary operator

[tool.isort]
profile = "black"
line_length = 120
known_third_party = [
    "jsonschema",
    "pyyaml",
    "voyageai",
    "openai>=1.0",
    "cohere>=5.0",
    "google-generativeai",
    "google-cloud-aiplatform",
    "google-cloud-firestore",
    "asyncpg",
    "pgvector",
    "google-auth",
    "starlette",
    "uvicorn",
    "google-auth"
]

[tool.mypy]
mypy_path = ["src", "src/python"]
files = ["src", "src/python"]
ignore_missing_imports = true
no_implicit_optional = false
scripts_are_modules = true
exclude = [
    "build/",
    "dist/",
    ".*.egg-info/",
]

[tool.coverage.run]
branch = true
source =["mcp_project_context_server"]
````
