# The Euphony Protocol Addendum

>  The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
>  NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and
>  "OPTIONAL" in this document are to be interpreted as described in
>  [RFC2119](https://tools.ietf.org/html/rfc2119).

## Introduction

The Euphony Protocol Addendum contains useful, but optional hints for implementing certain things. Anything that doesn't affect the protocol itself too heavily (mostly federation-related cases) is added to this document for additional refference.

## Permissions

Permissions are handled by an implementation of OAuth 2.0.

### List of permission scopes

#### read

- read:account
- read:server
- read:instance
- read:message

#### write

- write:account
- write:server
- write:instance
- write:message

