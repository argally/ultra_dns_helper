$ORIGIN {{domain}}.
@	3600	IN	SOA pdns1.ultradns.net.  (
	        {{serial}}	;Serial
			60		    ;Refresh
			60		    ;Retry
			604800		;Expire
			300		    ;Minimum
		)
@	3600	IN	NS	dns2.p06.nsone.net.
@	3600	IN	NS	dns3.p06.nsone.net.
@	3600	IN	NS	pdns1.ultradns.net.
@	3600	IN	NS	pdns2.ultradns.net.
@	3600	IN	NS	pdns3.ultradns.org.
@	3600	IN	NS	dns1.p06.nsone.net.

